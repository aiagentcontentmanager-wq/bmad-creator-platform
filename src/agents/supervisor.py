"""Supervisor agent — monitors and manages all child agents."""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.agents.base import BaseAgent, AgentStatus

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Monitors and manages all child agents, ensuring system health and
    enforcing policies.

    Inherits from BaseAgent so it can itself be supervised if needed.
    """

    def __init__(self):
        super().__init__("SupervisorAgent")
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        self.policies: Dict[str, Any] = {}
        self.alerts: List[Dict[str, Any]] = []

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process supervisor tasks."""
        action = task.get("action", "status")

        if action == "status":
            return self.get_all_agents_status()
        elif action == "health_check_all":
            return await self._health_check_all()
        elif action == "register":
            agent = task.get("agent")
            agent_id = task.get("agent_id")
            if agent:
                await self.register_agent(agent)
            elif agent_id:
                await self.register_agent_by_id(agent_id)
            return {"registered": True}
        elif action == "restart":
            agent_id = task.get("agent_id")
            if agent_id:
                await self.restart_agent(agent_id)
            return {"restarted": agent_id}
        else:
            return {"error": f"Unknown action: {action}"}

    async def start(self):
        """Start the supervisor."""
        await super().start()
        logger.info("SupervisorAgent started, ready to manage agents")

    async def register_agent(self, agent: BaseAgent):
        """Register a BaseAgent instance with the supervisor."""
        agent_id = agent.agent_id
        self.agents[agent_id] = agent
        self.agent_status[agent_id] = agent.get_status()
        logger.info(f"Agent {agent_id} registered with supervisor")

    async def register_agent_by_id(self, agent_id: str, initial_status: str = "INIT"):
        """Register an agent by ID (for agents not yet instantiated)."""
        self.agent_status[agent_id] = AgentStatus(
            agent_id=agent_id,
            status=initial_status,
            health="unknown",
            last_checked="never",
            metrics={},
        )
        logger.info(f"Agent {agent_id} registered with status {initial_status}")

    async def health_check_agent(self, agent_id: str) -> Dict[str, Any]:
        """Perform a health check on a specific agent using its BaseAgent interface."""
        if agent_id in self.agents:
            # Use the BaseAgent health_check() interface
            agent = self.agents[agent_id]
            try:
                result = await agent.health_check()
                # Update tracked status
                self.agent_status[agent_id] = agent.get_status()
                logger.info(f"Health check for agent {agent_id}: {result.get('health')}")
                return result
            except Exception as e:
                logger.error(f"Health check failed for agent {agent_id}: {e}")
                self.agent_status[agent_id].health = "error"
                self.agent_status[agent_id].error_count += 1
                return {"agent_id": agent_id, "health": "error", "error": str(e)}
        elif agent_id in self.agent_status:
            # Agent registered by ID but not instantiated
            return {
                "agent_id": agent_id,
                "status": self.agent_status[agent_id].status,
                "health": self.agent_status[agent_id].health,
                "last_checked": self.agent_status[agent_id].last_checked,
            }
        else:
            raise ValueError(f"Agent {agent_id} not found")

    async def _health_check_all(self) -> Dict[str, Any]:
        """Health check all registered agents."""
        results = {}
        for agent_id in list(self.agent_status.keys()):
            try:
                results[agent_id] = await self.health_check_agent(agent_id)
            except Exception as e:
                results[agent_id] = {"health": "error", "error": str(e)}
                await self.handle_degraded_agent(agent_id)
        return results

    async def monitor_agents(self, interval: int = 60):
        """Continuously monitor all registered agents."""
        logger.info(f"Starting agent monitoring loop (interval={interval}s)")
        while self._running:
            logger.info("Starting health check for all agents")
            for agent_id in list(self.agent_status.keys()):
                try:
                    await self.health_check_agent(agent_id)
                except Exception as e:
                    logger.error(f"Health check failed for agent {agent_id}: {e}")
                    await self.handle_degraded_agent(agent_id)

            await asyncio.sleep(interval)

    async def handle_degraded_agent(self, agent_id: str):
        """Handle an agent that is in a degraded state."""
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")

        self.agent_status[agent_id].status = "DEGRADED"
        logger.warning(f"Agent {agent_id} is degraded")

        # Generate alert with real timestamp
        alert = {
            "agent_id": agent_id,
            "status": "DEGRADED",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Agent {agent_id} is in a degraded state",
        }
        self.alerts.append(alert)

        # Attempt to restart the agent
        await self.restart_agent(agent_id)

    async def restart_agent(self, agent_id: str):
        """Restart a specific agent."""
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")

        logger.info(f"Restarting agent {agent_id}")
        self.agent_status[agent_id].status = "RECOVERING"

        if agent_id in self.agents:
            try:
                await self.agents[agent_id].stop()
                await asyncio.sleep(2)
                await self.agents[agent_id].start()
                self.agent_status[agent_id] = self.agents[agent_id].get_status()
            except Exception as e:
                logger.error(f"Failed to restart agent {agent_id}: {e}")
                self.agent_status[agent_id].status = "ERROR"
                self.agent_status[agent_id].error_count += 1
                return
        else:
            # Simulate restart for non-instantiated agents
            await asyncio.sleep(3)

        self.agent_status[agent_id].status = "READY"
        logger.info(f"Agent {agent_id} restarted successfully")

    async def load_policies(self, policy_file: str):
        """Load policies from a YAML file."""
        try:
            import yaml

            with open(policy_file, "r") as f:
                self.policies = yaml.safe_load(f) or {}
            logger.info(f"Policies loaded from {policy_file}")
        except FileNotFoundError:
            logger.warning(f"Policy file {policy_file} not found, using defaults")
            self.policies = {
                "moderation": {
                    "max_nudity_score": 0.85,
                    "max_toxicity_score": 0.90,
                    "auto_pause_threshold": 5,
                    "escalate_to": "governance",
                }
            }
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            self.policies = {}

    async def evaluate_policies(self, agent_id: str) -> bool:
        """Evaluate policies for a specific agent."""
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")

        agent_stat = self.agent_status[agent_id]

        # Check error count against auto_pause_threshold
        moderation = self.policies.get("moderation", {})
        auto_pause_threshold = moderation.get("auto_pause_threshold", 5)

        if agent_stat.error_count >= auto_pause_threshold:
            logger.warning(
                f"Agent {agent_id} exceeded error threshold "
                f"({agent_stat.error_count} >= {auto_pause_threshold})"
            )
            return False

        # Check health status
        if agent_stat.health == "error":
            logger.warning(f"Agent {agent_id} is in error state")
            return False

        logger.info(f"Policy evaluation for agent {agent_id}: compliant")
        return True

    def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get the status of a specific agent."""
        if agent_id not in self.agent_status:
            raise ValueError(f"Agent {agent_id} not found")
        return self.agent_status[agent_id]

    def get_all_agents_status(self) -> Dict[str, Any]:
        """Get the status of all registered agents."""
        return {
            agent_id: {
                "status": status.status,
                "health": status.health,
                "last_checked": status.last_checked,
                "error_count": status.error_count,
                "metrics": status.metrics,
            }
            for agent_id, status in self.agent_status.items()
        }

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get a list of all alerts."""
        return self.alerts

    def get_alerts_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get alerts for a specific agent."""
        return [a for a in self.alerts if a.get("agent_id") == agent_id]
