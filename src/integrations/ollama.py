"""Ollama API client for local AI inference."""

import httpx
import logging
from typing import Optional, Dict, Any
from src.core.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, endpoint: Optional[str] = None, model: Optional[str] = None):
        self.endpoint = endpoint or settings.OLLAMA_ENDPOINT
        self.model = model or settings.OLLAMA_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using Ollama."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await self.client.post(f"{self.endpoint}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except httpx.ConnectError:
            logger.warning("Ollama not available at %s", self.endpoint)
            raise ConnectionError(f"Ollama not available at {self.endpoint}")
        except Exception as e:
            logger.error("Ollama error: %s", e)
            raise

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = await self.client.get(f"{self.endpoint}/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()
