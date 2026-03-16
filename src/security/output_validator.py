
import re
from typing import List, Dict, Any

class AIOutputValidator:
    """
    🔒 AI OUTPUT VALIDATOR
    Prevents AI from leaking sensitive information
    """
    
    SENSITIVE_PATTERNS = [
        # API Keys & Secrets
        r"sk-[a-zA-Z0-9]{32,}",  # OpenAI keys
        r"ghp_[a-zA-Z0-9]{36}",   # GitHub tokens
        r"AKIA[0-9A-Z]{16}",      # AWS keys
        
        # Environment Variables
        r"process\.env\.[A-Z_]+",
        r"\$\{?[A-Z_]+\}?",
        
        # Database Credentials
        r"postgres://[^:]+:[^@]+@",
        r"mysql://[^:]+:[^@]+@",
        
        # Internal System Paths
        r"/root/",
        r"/home/[^/]+/",
        r"C:\\Users\\[^\\]+\\"
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p) for p in self.SENSITIVE_PATTERNS]

    def validate(self, ai_output: str) -> Dict[str, Any]:
        detected_leaks = []
        sanitized_output = ai_output

        for pattern in self.compiled_patterns:
            matches = pattern.findall(ai_output)
            if matches:
                detected_leaks.extend(matches)
                sanitized_output = pattern.sub('[REDACTED]', sanitized_output)

        return {
            "is_safe": len(detected_leaks) == 0,
            "sanitized_output": sanitized_output,
            "detected_leaks": detected_leaks,
        }
