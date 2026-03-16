
import time
import json
import logging
from typing import Optional
from typing import Any
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIRateLimiter:
    """
    🔒 AI ENDPOINT RATE LIMITING
    Prevents abuse and automated attacks
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.window_size = 15 * 60  # 15 minutes in seconds
        self.max_requests = 50       # max 50 requests per window
        
    def check_limit(self, key: str) -> bool:
        """
        Check if the limit has been reached for the given key (e.g., user_id or ip).
        Returns True if request is allowed, False if blocked.
        """
        current_time = int(time.time())
        window_start = current_time - self.window_size
        
        # Remove old requests
        self.redis.zremrangebyscore(f"rate_limit:{key}", 0, window_start)
        
        # Count requests in window
        request_count = self.redis.zcard(f"rate_limit:{key}")
        
        if request_count >= self.max_requests:
            return False
            
        # Add current request
        self.redis.zadd(f"rate_limit:{key}", {str(current_time): current_time})
        self.redis.expire(f"rate_limit:{key}", self.window_size)
        
        return True

    def log_request(self, params: Dict[str, Any]):
        """
        Audit Logger for AI Requests
        """
        tenant_id = params.get("tenant_id", "unknown")
        # Keep last 30 days
        thirty_days_ago = int(time.time()) - (30 * 24 * 60 * 60)
        
        # Use a sorted set for logs per tenant to easily prune old logs
        # Score is timestamp, Member is JSON payload
        self.redis.zadd(
            f"ai_audit:{tenant_id}", 
            {json.dumps(params): int(time.time())}
        )
        self.redis.zremrangebyscore(f"ai_audit:{tenant_id}", 0, thirty_days_ago)

