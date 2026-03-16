"""Content generation agent for the BMAD Creator Management Platform."""

import logging
import json
import random
from typing import Dict, Any, List, Optional

from src.agents.base import BaseAgent
from src.core.config import settings
from src.security.input_sanitizer import PromptInjectionDetector
from src.security.output_validator import AIOutputValidator

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """Generates content variants for creators using AI or template fallback."""

    STYLE_PROMPTS = {
        "casual": "Write in a casual, friendly, conversational tone. Use everyday language and a relaxed vibe.",
        "professional": "Write in a polished, professional tone. Be clear, concise, and engaging.",
        "playful": "Write in a fun, playful, flirty tone. Use emojis, slang, and be light-hearted.",
    }

    CONTENT_TYPE_TEMPLATES = {
        "caption": {
            "casual": [
                "Hey lovelies! Just wanted to share this moment with you all {topic}",
                "Living my best life and wanted you to be part of it {topic}",
                "No filter needed when you feel this good {topic}",
            ],
            "professional": [
                "Excited to share this with my amazing community. {topic}",
                "Another day, another opportunity to create something special. {topic}",
                "Thank you for being part of this journey. {topic}",
            ],
            "playful": [
                "Okay but can we talk about this?? {topic} Drop a comment if you agree!",
                "POV: You're having the best day ever {topic}",
                "This is your sign to treat yourself today {topic}",
            ],
        },
        "message": {
            "casual": [
                "Hey! Thanks for reaching out. {topic} Would love to chat more!",
                "Hi there! So glad you messaged me. {topic}",
                "Hey you! Thanks for stopping by. {topic}",
            ],
            "professional": [
                "Thank you for your message. {topic} I appreciate your support.",
                "I appreciate you reaching out. {topic} Looking forward to connecting.",
                "Thanks for your interest. {topic} I'm happy to help.",
            ],
            "playful": [
                "Hiii! You just made my day by messaging me {topic}",
                "OMG yes! {topic} You're the best for reaching out!",
                "Ahh love this! {topic} Can't wait to hear more from you!",
            ],
        },
        "bio": {
            "casual": [
                "Just a regular person sharing the good vibes {topic} Welcome to my world!",
                "Living life on my own terms. {topic} Thanks for being here!",
                "Here for a good time, not a long time. {topic}",
            ],
            "professional": [
                "Content creator and entrepreneur. {topic} Welcome to my page.",
                "Building a community around shared interests. {topic}",
                "Passionate creator sharing exclusive content. {topic}",
            ],
            "playful": [
                "Your daily dose of fun and chaos {topic} Welcome!",
                "Professional overthinker, part-time content queen {topic}",
                "Life's too short to be boring {topic} Let's make memories!",
            ],
        },
    }

    def __init__(self):
        super().__init__("ContentAgent")
        self.injection_detector = PromptInjectionDetector()
        self.output_validator = AIOutputValidator()
        self._ollama_url = getattr(settings, "OLLAMA_URL", "http://localhost:11434/api/generate")
        self._openrouter_api_key = getattr(settings, "OPENROUTER_API_KEY", None)
        self._openrouter_base_url = getattr(settings, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point from API."""
        creator_id = task.get("creator_id")
        content_type = task.get("content_type", "caption")
        topic = task.get("topic", "")
        style = task.get("style", "casual")
        persona = task.get("persona", {})

        if not creator_id:
            return {"error": "creator_id is required", "variants": []}

        # Check input for injection attempts
        injection_result = self.injection_detector.detect(topic)
        if not injection_result["is_safe"]:
            logger.warning(
                f"Prompt injection detected for creator {creator_id}: "
                f"{injection_result['risk_level']}"
            )
            return {
                "error": "Input blocked: potential prompt injection detected",
                "risk_level": injection_result["risk_level"],
                "variants": [],
            }

        # Build prompt based on content type, style, and persona
        prompt = self._build_prompt(content_type, topic, style, persona)

        # Generate 3 variants
        variants = []
        for i in range(3):
            variant_style = style
            if i == 1 and style == "casual":
                variant_style = "professional"
            elif i == 2 and style == "casual":
                variant_style = "playful"

            content_text = await self._call_ai(prompt, variant_style)

            # Validate output
            output_result = self.output_validator.validate(content_text)
            if not output_result["is_safe"]:
                logger.warning(
                    f"Sensitive content detected in AI output for creator {creator_id}"
                )
                content_text = output_result["sanitized_output"]

            variants.append(
                {
                    "style": variant_style,
                    "content": content_text,
                    "safe": output_result["is_safe"],
                }
            )

        return {
            "creator_id": creator_id,
            "content_type": content_type,
            "topic": topic,
            "variants": variants,
        }

    def _build_prompt(
        self, content_type: str, topic: str, style: str, persona: Dict[str, Any]
    ) -> str:
        """Build a persona-based prompt for content generation."""
        style_instruction = self.STYLE_PROMPTS.get(
            style, self.STYLE_PROMPTS["casual"]
        )

        persona_context = ""
        if persona:
            name = persona.get("display_name", "the creator")
            personality = persona.get("personality", "friendly and engaging")
            interests = persona.get("interests", [])
            voice_tone = persona.get("voice_tone", style)

            persona_context = (
                f"You are writing as {name}, who is {personality}. "
            )
            if interests:
                persona_context += f"They are interested in {', '.join(interests)}. "
            persona_context += f"Their preferred voice tone is {voice_tone}. "

        topic_context = f" about: {topic}" if topic else ""

        prompt = (
            f"{persona_context}"
            f"Write a {content_type}{topic_context}. "
            f"{style_instruction} "
            f"Keep it under 280 characters for captions or 500 characters for messages. "
            f"Do not include hashtags unless specifically relevant. "
            f"Make it feel authentic and personal."
        )

        return prompt

    async def _call_ai(self, prompt: str, style: str = "casual") -> str:
        """Try OpenRouter first, then Ollama, then fall back to template."""
        # Try OpenRouter first
        if self._openrouter_api_key:
            try:
                result = await self._call_openrouter(prompt)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"OpenRouter call failed: {e}")

        # Try Ollama second
        try:
            result = await self._call_ollama(prompt)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Ollama call failed: {e}")

        # Fall back to template
        return self._generate_from_template(prompt, style)

    async def _call_openrouter(self, prompt: str) -> Optional[str]:
        """Call OpenRouter API for content generation."""
        import httpx

        headers = {
            "Authorization": f"Bearer {self._openrouter_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a creative content writer for a social media creator. "
                        "Generate engaging, authentic content. Be concise and natural."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 300,
            "temperature": 0.8,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self._openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call local Ollama instance for content generation."""
        import httpx

        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.8, "num_predict": 300},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self._ollama_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    def _generate_from_template(self, prompt: str, style: str) -> str:
        """Generate content from templates when AI providers are unavailable."""
        # Extract content type from the prompt
        content_type = "caption"
        for ct in ["caption", "message", "bio"]:
            if ct in prompt.lower():
                content_type = ct
                break

        # Extract topic from prompt
        topic = ""
        if "about:" in prompt:
            topic_part = prompt.split("about:")[1].split(".")[0].strip()
            topic = topic_part if topic_part else ""

        templates = self.CONTENT_TYPE_TEMPLATES.get(content_type, {}).get(
            style, self.CONTENT_TYPE_TEMPLATES["caption"]["casual"]
        )

        template = random.choice(templates)
        return template.format(topic=topic)
