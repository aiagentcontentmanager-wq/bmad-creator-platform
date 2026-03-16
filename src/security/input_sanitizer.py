
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator

class PromptInjectionDetector:
    """
    🔒 PROMPT INJECTION PROTECTION
    Detects and blocks common prompt injection patterns
    """
    
    DANGEROUS_PATTERNS = [
        # Instruction Override Attempts
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts)",
        r"forget\s+(all\s+)?(previous|prior|above)\s+instructions",
        
        # Role Manipulation
        r"you\s+are\s+now\s+a\s+",
        r"act\s+as\s+(a\s+)?(?!assistant)",
        r"pretend\s+to\s+be",
        r"roleplay\s+as",
        
        # System Prompt Extraction
        r"show\s+(me\s+)?(your\s+)?(system\s+)?prompt",
        r"what\s+(are|is)\s+your\s+(initial|system|original)\s+instructions",
        r"repeat\s+your\s+instructions",
        
        # Data Exfiltration
        r"show\s+(me\s+)?(all\s+)?(api\s+)?keys",
        r"list\s+(all\s+)?(environment\s+)?variables",
        r"print\s+(all\s+)?(secrets|tokens|passwords)",
        
        # Delimiter Injection
        r"---\s*END\s+OF\s+SYSTEM",
        r"<\|im_end\|>",
        r"<\|endoftext\|>",
        
        # JSON/Code Injection in AI context
        r"}\s*,?\s*{[\s\S]*\"role\"\s*:\s*\"system\""
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS]

    def detect(self, input_text: str) -> Dict[str, Any]:
        detected_patterns = []
        
        for pattern in self.compiled_patterns:
            if pattern.search(input_text):
                # Reverse lookup for the raw pattern string is tricky with regex objects, 
                # so we just add the match content or a generic warning
                detected_patterns.append(pattern.pattern)

        risk_level = self.calculate_risk_level(len(detected_patterns))
        
        return {
            "is_safe": len(detected_patterns) == 0,
            "detected_patterns": detected_patterns,
            "sanitized_input": self.sanitize(input_text) if detected_patterns else input_text,
            "risk_level": risk_level,
        }

    def calculate_risk_level(self, detection_count: int) -> str:
        if detection_count >= 3: return 'CRITICAL'
        if detection_count == 2: return 'HIGH'
        if detection_count == 1: return 'MEDIUM'
        return 'SAFE'

    def sanitize(self, input_text: str) -> str:
        # Option 1: Block completely (recommended for critical systems)
        return '[BLOCKED: Potential prompt injection detected]'

class SafeUserInput(BaseModel):
    message: str
    metadata: Dict[str, Any]

    @validator('message')
    def check_safety(cls, v):
        detector = PromptInjectionDetector()
        result = detector.detect(v)
        if not result["is_safe"]:
             raise ValueError(f"Potential prompt injection detected: {result['detected_patterns']}")
        return v
