"""Creator assistant agent — provides response suggestions for creators."""

import logging
import random
from typing import Dict, Any, List, Optional

from src.agents.base import BaseAgent
from src.security.input_sanitizer import PromptInjectionDetector
from src.security.output_validator import AIOutputValidator

logger = logging.getLogger(__name__)


# Common response templates for fallback
RESPONSE_TEMPLATES = {
    "greeting": [
        "Hey there! Thanks for reaching out!",
        "Hi! So glad to hear from you!",
        "Hello! Welcome!",
    ],
    "thanks": [
        "Thank you so much for your support! It means the world to me.",
        "You're amazing! Thanks for being part of this journey.",
        "I really appreciate you! Thanks for reaching out.",
    ],
    "upsell": [
        "If you enjoyed that, you should check out my exclusive content!",
        "Want to see more? I have some special stuff just for subscribers.",
        "Love the energy! You might enjoy my premium content too.",
    ],
    "question_response": [
        "Great question! Let me think about that for you.",
        "That's a really good question! Here's what I think...",
        "Ooh, I love that question! So basically...",
    ],
    "boundary": [
        "Thanks for understanding! I really appreciate your respect.",
        "I appreciate you asking! Let's keep things in this lane.",
        "That's sweet of you to ask, but I'd prefer to keep things as they are.",
    ],
    "encouragement": [
        "You've got this! Keep doing your thing!",
        "Don't give up! You're doing amazing!",
        "Sending you good vibes! You're awesome!",
    ],
    "farewell": [
        "Thanks for chatting! Talk soon!",
        "It was great hearing from you! Take care!",
        "Bye for now! Don't be a stranger!",
    ],
}

# Tone modifiers applied to templates
TONE_MODIFIERS = {
    "casual": {
        "prefix": ["Hey! ", "Hi! ", "Oh "],
        "suffix": [" 😊", " 💕", "!"],
    },
    "professional": {
        "prefix": ["", "Thank you. ", "I appreciate that. "],
        "suffix": [".", ".", ""],
    },
    "playful": {
        "prefix": ["OMG ", "Ahh! ", "Hehe "],
        "suffix": [" 😜", " 💖", " ✨"],
    },
}


class CreatorAssistant(BaseAgent):
    """
    Provides response suggestions for a creator.

    This agent NEVER sends messages on behalf of the creator. It only generates
    suggested responses that the creator can review and choose to send.
    """

    def __init__(self):
        super().__init__("CreatorAssistant")
        self.injection_detector = PromptInjectionDetector()
        self.output_validator = AIOutputValidator()

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate response suggestions for a creator.

        task = {
            "creator_id": "...",
            "fan_identifier": "...",
            "fan_message": "...",
            "conversation_history": [...],
            "persona": {...},
            "context": {...},
        }

        Returns: {
            "suggestion": "...",
            "tone": "...",
            "alternatives": [...],
            "category": "...",
        }
        """
        creator_id = task.get("creator_id")
        fan_identifier = task.get("fan_identifier", "fan")
        fan_message = task.get("fan_message", "")
        conversation_history = task.get("conversation_history", [])
        persona = task.get("persona", {})
        context = task.get("context", {})

        if not creator_id:
            return {"error": "creator_id is required"}

        if not fan_message:
            return {"error": "fan_message is required"}

        # Check for injection attempts
        injection_result = self.injection_detector.detect(fan_message)
        if not injection_result["is_safe"]:
            logger.warning(
                f"Prompt injection detected in fan message for creator {creator_id}"
            )
            return {
                "error": "Input blocked: potential prompt injection detected",
                "risk_level": injection_result["risk_level"],
            }

        # Analyze the fan message to determine intent/category
        category = self._categorize_message(fan_message, conversation_history)

        # Get the creator's preferred tone from persona
        tone = persona.get("voice_tone", "casual")

        # Generate suggestions
        suggestion = self._build_suggestion(
            fan_message, category, tone, persona, conversation_history
        )
        alternatives = self._build_alternatives(
            fan_message, category, tone, persona, suggestion
        )

        return {
            "creator_id": creator_id,
            "fan_identifier": fan_identifier,
            "suggestion": suggestion,
            "tone": tone,
            "category": category,
            "alternatives": alternatives,
            "note": "These are suggestions only. The creator must choose to send any response.",
        }

    def _categorize_message(
        self, fan_message: str, conversation_history: List[Dict[str, str]]
    ) -> str:
        """Categorize the fan's message to pick appropriate response templates."""
        message_lower = fan_message.lower().strip()

        # Check if it's the start of a conversation
        is_first_message = len(conversation_history) == 0

        if is_first_message:
            return "greeting"

        # Detect question
        if "?" in fan_message or any(
            q in message_lower
            for q in ["how", "what", "when", "where", "why", "can you", "do you"]
        ):
            return "question_response"

        # Detect thank you / appreciation
        if any(
            w in message_lower
            for w in ["thank", "thanks", "appreciate", "love your", "amazing"]
        ):
            return "thanks"

        # Detect farewell
        if any(
            w in message_lower
            for w in ["bye", "goodbye", "see you", "talk later", "gotta go"]
        ):
            return "farewell"

        # Detect boundary-pushing
        if any(
            w in message_lower
            for w in ["meet up", "personal", "phone number", "real name", "address"]
        ):
            return "boundary"

        # Detect encouragement need
        if any(
            w in message_lower
            for w in ["sad", "bad day", "struggling", "tough", "difficult"]
        ):
            return "encouragement"

        # Default to upsell if conversation is going well
        if len(conversation_history) >= 3:
            return "upsell"

        return "greeting"

    def _build_suggestion(
        self,
        fan_message: str,
        category: str,
        tone: str,
        persona: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """Build the primary response suggestion."""
        templates = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES["greeting"])
        base_response = random.choice(templates)

        # Apply tone modifiers
        modifiers = TONE_MODIFIERS.get(tone, TONE_MODIFIERS["casual"])
        prefix = random.choice(modifiers["prefix"])
        suffix = random.choice(modifiers["suffix"])

        # Personalize with creator's display name if available
        display_name = persona.get("display_name", "")

        # Add context-aware elements
        if category == "question_response":
            # Keep it generic since we don't have AI in fallback
            suggestion = f"{prefix}{base_response}{suffix}"
        elif category == "greeting" and display_name:
            suggestion = f"{prefix}{base_response} I'm {display_name}!{suffix}"
        else:
            suggestion = f"{prefix}{base_response}{suffix}"

        return suggestion

    def _build_alternatives(
        self,
        fan_message: str,
        category: str,
        tone: str,
        persona: Dict[str, Any],
        primary_suggestion: str,
    ) -> List[str]:
        """Build alternative response suggestions."""
        templates = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES["greeting"])
        modifiers = TONE_MODIFIERS.get(tone, TONE_MODIFIERS["casual"])

        alternatives = []
        used_templates = set()

        for _ in range(2):
            # Pick a template not already used
            available = [t for t in templates if t not in used_templates]
            if not available:
                available = templates

            template = random.choice(available)
            used_templates.add(template)

            prefix = random.choice(modifiers["prefix"])
            suffix = random.choice(modifiers["suffix"])
            alt = f"{prefix}{template}{suffix}"

            # Don't duplicate the primary suggestion
            if alt != primary_suggestion:
                alternatives.append(alt)

        # If we couldn't get 2 distinct alternatives, generate from a different category
        while len(alternatives) < 2:
            fallback_category = random.choice(
                [c for c in RESPONSE_TEMPLATES.keys() if c != category]
            )
            fallback_templates = RESPONSE_TEMPLATES[fallback_category]
            template = random.choice(fallback_templates)
            prefix = random.choice(modifiers["prefix"])
            suffix = random.choice(modifiers["suffix"])
            alt = f"{prefix}{template}{suffix}"
            if alt not in alternatives and alt != primary_suggestion:
                alternatives.append(alt)

        return alternatives[:2]
