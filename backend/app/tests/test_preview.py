"""Tests for URL preview screenshot service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

from app.services.preview import PreviewService


class TestPreviewService:
    """Tests for PreviewService."""

    def test_service_initialization(self):
        """Test that preview service initializes correctly."""
        service = PreviewService()
        assert service._client is None
        assert service._bucket is None
        assert service._browser is None

    @pytest.mark.asyncio
    async def test_generate_screenshot_no_browser(self):
        """Test screenshot generation when browser is unavailable."""
        service = PreviewService()

        # Mock browser to return None
        with patch.object(service, '_get_browser', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            result = await service.generate_screenshot("https://example.com")
            assert result is None

    @pytest.mark.asyncio
    async def test_generate_screenshot_success(self):
        """Test successful screenshot generation."""
        service = PreviewService()

        # Create mock browser and page
        mock_page = AsyncMock()
        mock_page.screenshot = AsyncMock(return_value=b"fake_png_data")

        mock_browser = AsyncMock()
        mock_browser.newPage = AsyncMock(return_value=mock_page)

        with patch.object(service, '_get_browser', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_browser

            result = await service.generate_screenshot("https://example.com")

            assert result == b"fake_png_data"
            mock_page.setViewport.assert_called_once()
            mock_page.goto.assert_called_once()
            mock_page.screenshot.assert_called_once()
            mock_page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_screenshot_error(self):
        """Test screenshot generation when page fails to load."""
        service = PreviewService()

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Page load failed"))

        mock_browser = AsyncMock()
        mock_browser.newPage = AsyncMock(return_value=mock_page)

        with patch.object(service, '_get_browser', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_browser

            result = await service.generate_screenshot("https://example.com")

            assert result is None
            mock_page.close.assert_called_once()  # Page should still be closed

    @pytest.mark.asyncio
    async def test_store_screenshot_success(self):
        """Test successful screenshot storage in GridFS."""
        service = PreviewService()

        mock_bucket = AsyncMock()
        mock_bucket.upload_from_stream = AsyncMock(return_value=ObjectId())

        with patch.object(service, '_get_db', new_callable=AsyncMock) as mock_db:
            mock_db.return_value = mock_bucket

            result = await service.store_screenshot(
                b"png_data",
                "abc123",
                "https://example.com"
            )

            assert result is not None
            mock_bucket.upload_from_stream.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_screenshot_error(self):
        """Test screenshot storage failure."""
        service = PreviewService()

        mock_bucket = AsyncMock()
        mock_bucket.upload_from_stream = AsyncMock(
            side_effect=Exception("Storage failed")
        )

        with patch.object(service, '_get_db', new_callable=AsyncMock) as mock_db:
            mock_db.return_value = mock_bucket

            result = await service.store_screenshot(
                b"png_data",
                "abc123",
                "https://example.com"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_get_screenshot_success(self):
        """Test successful screenshot retrieval."""
        service = PreviewService()

        mock_stream = AsyncMock()
        mock_stream.read = AsyncMock(return_value=b"png_data")

        mock_bucket = AsyncMock()
        mock_bucket.open_download_stream = AsyncMock(return_value=mock_stream)

        with patch.object(service, '_get_db', new_callable=AsyncMock) as mock_db:
            mock_db.return_value = mock_bucket

            result = await service.get_screenshot(str(ObjectId()))

            assert result == b"png_data"

    @pytest.mark.asyncio
    async def test_get_screenshot_not_found(self):
        """Test screenshot retrieval when file doesn't exist."""
        service = PreviewService()

        mock_bucket = AsyncMock()
        mock_bucket.open_download_stream = AsyncMock(
            side_effect=Exception("File not found")
        )

        with patch.object(service, '_get_db', new_callable=AsyncMock) as mock_db:
            mock_db.return_value = mock_bucket

            result = await service.get_screenshot(str(ObjectId()))

            assert result is None

    @pytest.mark.asyncio
    async def test_delete_screenshot_success(self):
        """Test successful screenshot deletion."""
        service = PreviewService()

        mock_bucket = AsyncMock()
        mock_bucket.delete = AsyncMock()

        with patch.object(service, '_get_db', new_callable=AsyncMock) as mock_db:
            mock_db.return_value = mock_bucket

            result = await service.delete_screenshot(str(ObjectId()))

            assert result is True
            mock_bucket.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_screenshot_error(self):
        """Test screenshot deletion failure."""
        service = PreviewService()

        mock_bucket = AsyncMock()
        mock_bucket.delete = AsyncMock(side_effect=Exception("Delete failed"))

        with patch.object(service, '_get_db', new_callable=AsyncMock) as mock_db:
            mock_db.return_value = mock_bucket

            result = await service.delete_screenshot(str(ObjectId()))

            assert result is False

    @pytest.mark.asyncio
    async def test_generate_and_store(self):
        """Test combined generate and store operation."""
        service = PreviewService()

        file_id = str(ObjectId())

        with patch.object(
            service, 'generate_screenshot', new_callable=AsyncMock
        ) as mock_gen:
            with patch.object(
                service, 'store_screenshot', new_callable=AsyncMock
            ) as mock_store:
                mock_gen.return_value = b"png_data"
                mock_store.return_value = file_id

                result = await service.generate_and_store(
                    "https://example.com",
                    "abc123"
                )

                assert result == file_id
                mock_gen.assert_called_once()
                mock_store.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_and_store_generation_fails(self):
        """Test generate_and_store when screenshot generation fails."""
        service = PreviewService()

        with patch.object(
            service, 'generate_screenshot', new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = None

            result = await service.generate_and_store(
                "https://example.com",
                "abc123"
            )

            assert result is None
