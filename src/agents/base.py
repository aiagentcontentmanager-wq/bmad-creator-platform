"""Abstract base class for all BMAD agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentStatus:
    agent_id: str
    status: str = "INIT"
    health: str = "unknown"
    last_checked: str = "never"
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0


class BaseAgent(ABC):
    """All agents must inherit from this class."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = AgentStatus(agent_id=agent_id)
        self._running = False

    async def start(self):
        self._running = True
        self.status.status = "READY"
        self.status.health = "ok"
        logger.info(f"Agent {self.agent_id} started")

    async def stop(self):
        self._running = False
        self.status.status = "STOPPED"
        logger.info(f"Agent {self.agent_id} stopped")

    async def health_check(self) -> Dict[str, Any]:
        self.status.last_checked = datetime.utcnow().isoformat()
        return {
            "agent_id": self.agent_id,
            "status": self.status.status,
            "health": self.status.health,
            "last_checked": self.status.last_checked,
            "error_count": self.status.error_count,
        }

    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task. Must be implemented by subclasses."""
        pass

    def get_status(self) -> AgentStatus:
        return self.status
