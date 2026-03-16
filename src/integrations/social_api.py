"""Social media platform API integrations.

All publishers use official platform APIs only — no scraping.
Rate limiting is handled with exponential backoff (max 3 retries).
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_BACKOFF = 1.0  # seconds


class BasePublisher(ABC):
    """Abstract base class for social media publishers."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _request_with_backoff(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request with exponential backoff on rate-limit responses."""
        last_exception: Optional[Exception] = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.request(method, url, **kwargs)

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", BASE_BACKOFF * (2 ** (attempt - 1))))
                    logger.warning(
                        "Rate limited on %s %s (attempt %d/%d). Retrying in %ds",
                        method, url, attempt, MAX_RETRIES, retry_after,
                    )
                    await asyncio.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF * (2 ** (attempt - 1))
                    logger.warning(
                        "Server error %d on %s %s (attempt %d/%d). Retrying in %ds",
                        e.response.status_code, method, url, attempt, MAX_RETRIES, backoff,
                    )
                    await asyncio.sleep(backoff)
                    last_exception = e
                    continue
                raise
            except httpx.RequestError as e:
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF * (2 ** (attempt - 1))
                    logger.warning(
                        "Request error on %s %s (attempt %d/%d): %s. Retrying in %ds",
                        method, url, attempt, MAX_RETRIES, e, backoff,
                    )
                    await asyncio.sleep(backoff)
                    last_exception = e
                    continue
                raise

        # If we exhausted retries due to 429s, raise the last encountered exception
        if last_exception:
            raise last_exception
        raise RuntimeError(f"All {MAX_RETRIES} retry attempts exhausted for {method} {url}")

    @abstractmethod
    async def publish(self, **kwargs) -> Dict[str, Any]:
        """Publish content to the platform. Returns a result dict."""
        ...

    async def close(self):
        await self.client.aclose()


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------

class InstagramPublisher(BasePublisher):
    """Publish content to Instagram via the Instagram Graph API (v18.0)."""

    BASE_URL = "https://graph.instagram.com/v18.0"

    async def publish_image(
        self,
        caption: str,
        image_url: str,
        access_token: str,
    ) -> Dict[str, Any]:
        """Publish a single image post to Instagram.

        Uses the two-step process:
        1. Create a media container.
        2. Publish the container.
        """
        logger.info("Publishing image to Instagram (caption length=%d)", len(caption))

        try:
            # Step 1 — create container
            container_resp = await self._request_with_backoff(
                "POST",
                f"{self.BASE_URL}/me/media",
                data={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": access_token,
                },
            )
            container_id = container_resp.json().get("id")
            if not container_id:
                return {"success": False, "post_id": "", "error": "No container ID returned"}

            # Step 2 — publish container
            publish_resp = await self._request_with_backoff(
                "POST",
                f"{self.BASE_URL}/me/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": access_token,
                },
            )
            post_id = publish_resp.json().get("id", "")
            logger.info("Instagram image published successfully: %s", post_id)
            return {"success": True, "post_id": post_id, "error": ""}

        except Exception as e:
            logger.error("Instagram image publish failed: %s", e)
            return {"success": False, "post_id": "", "error": str(e)}

    async def publish_video(
        self,
        caption: str,
        video_url: str,
        access_token: str,
    ) -> Dict[str, Any]:
        """Publish a single video (reel) to Instagram.

        Uses the two-step process with a longer timeout for video processing.
        """
        logger.info("Publishing video to Instagram (caption length=%d)", len(caption))

        try:
            # Step 1 — create container (media_type=REELS for video)
            container_resp = await self._request_with_backoff(
                "POST",
                f"{self.BASE_URL}/me/media",
                data={
                    "video_url": video_url,
                    "caption": caption,
                    "media_type": "REELS",
                    "access_token": access_token,
                },
            )
            container_id = container_resp.json().get("id")
            if not container_id:
                return {"success": False, "post_id": "", "error": "No container ID returned"}

            # Step 2 — poll for video processing completion, then publish
            for _ in range(30):  # up to ~5 minutes with 10s intervals
                status_resp = await self._request_with_backoff(
                    "GET",
                    f"{self.BASE_URL}/{container_id}",
                    params={
                        "fields": "status_code",
                        "access_token": access_token,
                    },
                )
                status = status_resp.json().get("status_code")
                if status == "FINISHED":
                    break
                if status == "ERROR":
                    return {"success": False, "post_id": "", "error": "Video processing failed on Instagram side"}
                await asyncio.sleep(10)

            # Step 3 — publish container
            publish_resp = await self._request_with_backoff(
                "POST",
                f"{self.BASE_URL}/me/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": access_token,
                },
            )
            post_id = publish_resp.json().get("id", "")
            logger.info("Instagram video published successfully: %s", post_id)
            return {"success": True, "post_id": post_id, "error": ""}

        except Exception as e:
            logger.error("Instagram video publish failed: %s", e)
            return {"success": False, "post_id": "", "error": str(e)}

    async def publish(self, **kwargs) -> Dict[str, Any]:
        """Route to publish_image or publish_video based on kwargs."""
        if "video_url" in kwargs:
            return await self.publish_video(
                caption=kwargs.get("caption", ""),
                video_url=kwargs["video_url"],
                access_token=kwargs["access_token"],
            )
        return await self.publish_image(
            caption=kwargs.get("caption", ""),
            image_url=kwargs.get("image_url", ""),
            access_token=kwargs["access_token"],
        )


# ---------------------------------------------------------------------------
# Twitter / X
# ---------------------------------------------------------------------------

class TwitterPublisher(BasePublisher):
    """Publish tweets via the Twitter API v2."""

    BASE_URL = "https://api.twitter.com/2"

    async def publish_tweet(
        self,
        text: str,
        access_token: str,
    ) -> Dict[str, Any]:
        """Publish a tweet and return the result."""
        logger.info("Publishing tweet (length=%d)", len(text))

        try:
            response = await self._request_with_backoff(
                "POST",
                f"{self.BASE_URL}/tweets",
                json={"text": text},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )
            data = response.json()
            tweet_id = data.get("data", {}).get("id", "")
            logger.info("Tweet published successfully: %s", tweet_id)
            return {"success": True, "post_id": tweet_id, "error": ""}

        except Exception as e:
            logger.error("Tweet publish failed: %s", e)
            return {"success": False, "post_id": "", "error": str(e)}

    async def publish(self, **kwargs) -> Dict[str, Any]:
        """Publish a tweet."""
        return await self.publish_tweet(
            text=kwargs.get("text", ""),
            access_token=kwargs["access_token"],
        )


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

class TelegramPublisher(BasePublisher):
    """Send messages and photos via the Telegram Bot API."""

    def __init__(self, bot_token: Optional[str] = None):
        super().__init__()
        self.bot_token = bot_token
        if self.bot_token:
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        else:
            self.base_url = ""

    def set_bot_token(self, bot_token: str):
        """Set or update the bot token (needed when token is per-request)."""
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(
        self,
        chat_id: str,
        text: str,
    ) -> Dict[str, Any]:
        """Send a text message to a Telegram chat."""
        logger.info("Sending Telegram message to chat %s (length=%d)", chat_id, len(text))

        try:
            response = await self._request_with_backoff(
                "POST",
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                },
            )
            data = response.json()
            if data.get("ok"):
                message_id = str(data["result"]["message_id"])
                logger.info("Telegram message sent: %s", message_id)
                return {"success": True, "post_id": message_id, "error": ""}
            else:
                error_desc = data.get("description", "Unknown error")
                logger.error("Telegram API returned error: %s", error_desc)
                return {"success": False, "post_id": "", "error": error_desc}

        except Exception as e:
            logger.error("Telegram message send failed: %s", e)
            return {"success": False, "post_id": "", "error": str(e)}

    async def send_photo(
        self,
        chat_id: str,
        photo_url: str,
        caption: str = "",
    ) -> Dict[str, Any]:
        """Send a photo to a Telegram chat."""
        logger.info("Sending Telegram photo to chat %s", chat_id)

        try:
            payload: Dict[str, Any] = {
                "chat_id": chat_id,
                "photo": photo_url,
            }
            if caption:
                payload["caption"] = caption
                payload["parse_mode"] = "HTML"

            response = await self._request_with_backoff(
                "POST",
                f"{self.base_url}/sendPhoto",
                json=payload,
            )
            data = response.json()
            if data.get("ok"):
                message_id = str(data["result"]["message_id"])
                logger.info("Telegram photo sent: %s", message_id)
                return {"success": True, "post_id": message_id, "error": ""}
            else:
                error_desc = data.get("description", "Unknown error")
                logger.error("Telegram API returned error: %s", error_desc)
                return {"success": False, "post_id": "", "error": error_desc}

        except Exception as e:
            logger.error("Telegram photo send failed: %s", e)
            return {"success": False, "post_id": "", "error": str(e)}

    async def publish(self, **kwargs) -> Dict[str, Any]:
        """Route to send_message or send_photo based on kwargs."""
        if "photo_url" in kwargs:
            return await self.send_photo(
                chat_id=kwargs["chat_id"],
                photo_url=kwargs["photo_url"],
                caption=kwargs.get("caption", ""),
            )
        return await self.send_message(
            chat_id=kwargs["chat_id"],
            text=kwargs.get("text", ""),
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class PublisherFactory:
    """Return the appropriate publisher instance for a given platform name."""

    _registry: Dict[str, type] = {
        "instagram": InstagramPublisher,
        "twitter": TwitterPublisher,
        "telegram": TelegramPublisher,
    }

    @classmethod
    def create(cls, platform: str, **kwargs) -> BasePublisher:
        """Create a publisher for the given platform.

        Args:
            platform: One of 'instagram', 'twitter', 'telegram'.
            **kwargs: Extra keyword arguments forwarded to the publisher constructor.

        Returns:
            An instance of the corresponding publisher.

        Raises:
            ValueError: If the platform is not supported.
        """
        platform_key = platform.lower().strip()
        publisher_cls = cls._registry.get(platform_key)
        if publisher_cls is None:
            supported = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(f"Unsupported platform '{platform}'. Supported: {supported}")
        return publisher_cls(**kwargs)

    @classmethod
    def register(cls, name: str, publisher_cls: type):
        """Register a custom publisher class for a platform name."""
        cls._registry[name.lower().strip()] = publisher_cls
