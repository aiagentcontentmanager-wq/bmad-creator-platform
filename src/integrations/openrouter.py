"""OpenRouter API client for cloud AI inference."""

import httpx
import logging
from typing import Optional, Dict, Any, List
from src.core.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send a chat completion request to OpenRouter."""
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://bmad.local",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs,
        }

        try:
            response = await self.client.post(OPENROUTER_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error("OpenRouter API error: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("OpenRouter error: %s", e)
            raise

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Simple generate wrapper around chat."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages)

    async def is_available(self) -> bool:
        """Check if OpenRouter is configured."""
        return bool(self.api_key)

    async def close(self):
        await self.client.aclose()
