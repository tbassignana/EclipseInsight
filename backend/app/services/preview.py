"""
URL Preview Screenshot Service using Pyppeteer (Python Puppeteer).
Generates PNG screenshots of URLs and stores them in MongoDB GridFS.
"""

import asyncio
import io
from typing import Optional
from datetime import datetime, timezone
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from bson import ObjectId

from app.core.config import settings

logger = logging.getLogger(__name__)


class PreviewService:
    """Service for generating and storing URL preview screenshots."""

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._bucket: Optional[AsyncIOMotorGridFSBucket] = None
        self._browser = None
        self._browser_lock = asyncio.Lock()

    async def _get_db(self):
        """Get MongoDB client and GridFS bucket."""
        if self._client is None:
            self._client = AsyncIOMotorClient(settings.MONGODB_URL)
            db = self._client[settings.MONGODB_DB_NAME]
            self._bucket = AsyncIOMotorGridFSBucket(db, bucket_name="screenshots")
        return self._bucket

    async def _get_browser(self):
        """Get or create browser instance (lazy initialization)."""
        async with self._browser_lock:
            if self._browser is None:
                try:
                    from pyppeteer import launch
                    self._browser = await launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--single-process'
                        ]
                    )
                except Exception as e:
                    logger.error(f"Failed to launch browser: {e}")
                    return None
            return self._browser

    async def close_browser(self):
        """Close browser instance."""
        async with self._browser_lock:
            if self._browser:
                await self._browser.close()
                self._browser = None

    async def generate_screenshot(
        self,
        url: str,
        width: int = 1280,
        height: int = 720,
        timeout: int = 30000
    ) -> Optional[bytes]:
        """
        Generate a screenshot of a URL.

        Args:
            url: URL to capture
            width: Viewport width
            height: Viewport height
            timeout: Page load timeout in milliseconds

        Returns:
            PNG bytes or None on error
        """
        browser = await self._get_browser()
        if browser is None:
            logger.warning("Browser not available for screenshots")
            return None

        page = None
        try:
            page = await browser.newPage()
            await page.setViewport({'width': width, 'height': height})

            # Navigate to URL
            await page.goto(url, {
                'waitUntil': 'networkidle2',
                'timeout': timeout
            })

            # Take screenshot
            screenshot = await page.screenshot({
                'type': 'png',
                'clip': {
                    'x': 0,
                    'y': 0,
                    'width': width,
                    'height': height
                }
            })

            return screenshot

        except Exception as e:
            logger.error(f"Screenshot generation failed for {url}: {e}")
            return None

        finally:
            if page:
                await page.close()

    async def store_screenshot(
        self,
        screenshot_data: bytes,
        short_code: str,
        original_url: str
    ) -> Optional[str]:
        """
        Store screenshot in MongoDB GridFS.

        Args:
            screenshot_data: PNG bytes
            short_code: Short URL code
            original_url: Original URL

        Returns:
            GridFS file ID as string or None on error
        """
        try:
            bucket = await self._get_db()

            # Create file metadata
            metadata = {
                "short_code": short_code,
                "original_url": original_url,
                "content_type": "image/png",
                "created_at": datetime.now(timezone.utc)
            }

            # Upload to GridFS
            file_id = await bucket.upload_from_stream(
                f"preview_{short_code}.png",
                io.BytesIO(screenshot_data),
                metadata=metadata
            )

            return str(file_id)

        except Exception as e:
            logger.error(f"Failed to store screenshot: {e}")
            return None

    async def get_screenshot(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve screenshot from MongoDB GridFS.

        Args:
            file_id: GridFS file ID

        Returns:
            PNG bytes or None if not found
        """
        try:
            bucket = await self._get_db()
            stream = await bucket.open_download_stream(ObjectId(file_id))
            data = await stream.read()
            return data

        except Exception as e:
            logger.error(f"Failed to retrieve screenshot {file_id}: {e}")
            return None

    async def delete_screenshot(self, file_id: str) -> bool:
        """
        Delete screenshot from MongoDB GridFS.

        Args:
            file_id: GridFS file ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            bucket = await self._get_db()
            await bucket.delete(ObjectId(file_id))
            return True

        except Exception as e:
            logger.error(f"Failed to delete screenshot {file_id}: {e}")
            return False

    async def generate_and_store(
        self,
        url: str,
        short_code: str,
        width: int = 1280,
        height: int = 720
    ) -> Optional[str]:
        """
        Generate screenshot and store it.

        Args:
            url: URL to capture
            short_code: Short URL code
            width: Viewport width
            height: Viewport height

        Returns:
            GridFS file ID or None on error
        """
        screenshot = await self.generate_screenshot(url, width, height)
        if screenshot is None:
            return None

        return await self.store_screenshot(screenshot, short_code, url)


# Singleton instance
preview_service = PreviewService()
