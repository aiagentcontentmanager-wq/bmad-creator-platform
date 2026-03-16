#!/usr/bin/env python3
"""
ModelOrchestrator Implementation

This module is responsible for executing routed tasks, managing quotas,
rotating providers, and handling failures as specified in the architecture.
"""

import logging
from typing import Dict, List, Optional, Any
import uuid
import time
from dataclasses import dataclass

# Security Modules
from src.security.input_sanitizer import PromptInjectionDetector
from src.security.prompt_builder import SecurePromptBuilder
from src.security.output_validator import AIOutputValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task to be executed by the ModelOrchestrator."""
    task_id: str
    model_id: str
    tenant_id: str  # Added for multi-tenancy
    task_type: str
    payload: Dict[str, Any]
    priority: str = "normal"
    retries: int = 0


@dataclass
class Provider:
    """Represents an AI model provider."""
    name: str
    endpoint: str
    api_key: str
    max_quota: int
    current_quota: int = 0


class QuotaExceededError(Exception):
    """Raised when the quota for a model is exceeded."""
    pass


class ProviderUnavailableError(Exception):
    """Raised when a provider is unavailable."""
    pass


class SecurityViolationError(Exception):
    """Raised when a security check fails."""
    pass


class ModelOrchestrator:
    """
    The ModelOrchestrator is responsible for executing routed tasks,
    managing quotas, rotating providers, and handling failures.
    """

    def __init__(self, providers: List[Provider]):
        self.providers = providers
        self.quotas: Dict[str, int] = {}
        self.current_provider_index = 0
        self.failed_tasks: Dict[str, Task] = {}

        # Initialize Security Components
        self.injection_detector = PromptInjectionDetector()
        self.prompt_builder = SecurePromptBuilder()
        self.output_validator = AIOutputValidator()

    def check_quota(self, model_id: str) -> bool:
        """Check if the quota for a model is exceeded."""
        current_quota = self.quotas.get(model_id, 0)
        max_quota = 100  # Default max quota
        return current_quota < max_quota

    def update_quota(self, model_id: str):
        """Update the quota for a model."""
        current_quota = self.quotas.get(model_id, 0)
        self.quotas[model_id] = current_quota + 1

    def select_provider(self) -> Provider:
        """Select a provider using round-robin rotation."""
        provider = self.providers[self.current_provider_index]
        self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        return provider

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a task using the selected provider."""
        try:
            # 0. Validate Tenant
            if not task.tenant_id:
                raise ValueError("Missing tenant_id in Task")

            # 1. Security Check: Prompt Injection
            user_input = task.payload.get("prompt") or task.payload.get("message") or ""
            detection_result = self.injection_detector.detect(user_input)
            
            if not detection_result["is_safe"]:
                logger.critical(f"SECURITY ALERT: Prompt Injection detected for tenant {task.tenant_id}. Patterns: {detection_result['detected_patterns']}")
                raise SecurityViolationError(f"Potential prompt injection detected: {detection_result['detected_patterns']}")

            if not self.check_quota(task.model_id):
                raise QuotaExceededError(f"Quota exceeded for model {task.model_id}")

            provider = self.select_provider()
            logger.info(f"Executing task {task.task_id} for tenant {task.tenant_id} with provider {provider.name}")

            # 2. Secure Prompt Building
            secure_prompt = self.prompt_builder.build_secure_prompt(
                system_prompt="You are a helpful assistant.", # TODO: Load per-agent system prompt
                user_input=user_input,
                context={"tenant_id": task.tenant_id}
            )

            # Simulate task execution with provider
            # In a real scenario, we would send `secure_prompt` to the provider API
            simulated_response_text = f"Task {task.task_id} executed successfully. Echo: {user_input}"
            
            # 3. Security Check: Output Validation
            validation_result = self.output_validator.validate(simulated_response_text)
            
            if not validation_result["is_safe"]:
                logger.warning(f"SECURITY ALERT: Output leak detected for tenant {task.tenant_id}. Leaks: {validation_result['detected_leaks']}")
                # We return the sanitized output
                simulated_response_text = validation_result["sanitized_output"]

            result = {
                "task_id": task.task_id,
                "model_id": task.model_id,
                "tenant_id": task.tenant_id,
                "provider": provider.name,
                "status": "success",
                "result": simulated_response_text
            }

            self.update_quota(task.model_id)
            return result

        except Exception as error:
            await self.handle_error(error, task)
            raise

    async def handle_error(self, error: Exception, task: Task):
        """Handle errors during task execution."""
        logger.error(f"Error executing task {task.task_id}: {error}")

        if isinstance(error, SecurityViolationError):
             # Do not retry on security violations
             logger.error(f"Security violation for task {task.task_id}. Blocking task.")
             self.failed_tasks[task.task_id] = task

        elif isinstance(error, QuotaExceededError):
            logger.warning(f"Quota exceeded for task {task.task_id}")
            self.failed_tasks[task.task_id] = task

        elif isinstance(error, ProviderUnavailableError):
            logger.warning(f"Provider unavailable for task {task.task_id}")
            if task.retries < 3:
                task.retries += 1
                logger.info(f"Retrying task {task.task_id} (attempt {task.retries})")
                await self.execute_task(task)
            else:
                self.failed_tasks[task.task_id] = task

        else:
            logger.error(f"Unexpected error for task {task.task_id}: {error}")
            self.failed_tasks[task.task_id] = task

    def get_failed_tasks(self) -> Dict[str, Task]:
        """Get a list of failed tasks."""
        return self.failed_tasks


# Example usage
if __name__ == "__main__":
    import asyncio

    # Initialize providers
    providers = [
        Provider(
            name="Ollama",
            endpoint="http://localhost:11434",
            api_key="ollama_api_key",
            max_quota=100
        ),
        Provider(
            name="OpenRouter",
            endpoint="https://openrouter.ai/api/v1",
            api_key="openrouter_api_key",
            max_quota=100
        )
    ]

    # Initialize ModelOrchestrator
    orchestrator = ModelOrchestrator(providers)

    # Create a task
    task = Task(
        task_id=str(uuid.uuid4()),
        model_id="model_1",
        tenant_id="tenant_123",
        task_type="content_generation",
        payload={"prompt": "Generate content"}
    )

    # Execute the task
    async def main():
        try:
            result = await orchestrator.execute_task(task)
            print(f"Task executed successfully: {result}")
        except Exception as e:
            print(f"Task failed: {e}")

    asyncio.run(main())