"""Tests for QR code generation feature."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.url import ShortURL
from app.services.qrcode import generate_qr_code


class TestQRCodeService:
    """Tests for the QR code generation service."""

    def test_generate_qr_code_returns_png_bytes(self):
        """Test that generate_qr_code returns valid PNG bytes."""
        result = generate_qr_code("https://example.com/abc123")
        assert isinstance(result, bytes)
        # PNG files start with the magic bytes \x89PNG
        assert result[:4] == b"\x89PNG"

    def test_generate_qr_code_different_urls_produce_different_images(self):
        """Test that different URLs produce different QR codes."""
        qr1 = generate_qr_code("https://example.com/aaa")
        qr2 = generate_qr_code("https://example.com/bbb")
        assert qr1 != qr2

    def test_generate_qr_code_same_url_produces_same_image(self):
        """Test that the same URL produces the same QR code."""
        qr1 = generate_qr_code("https://example.com/same")
        qr2 = generate_qr_code("https://example.com/same")
        assert qr1 == qr2

    def test_generate_qr_code_custom_size(self):
        """Test that larger box_size produces a larger image."""
        small = generate_qr_code("https://example.com/test", size=5)
        large = generate_qr_code("https://example.com/test", size=20)
        # Larger box_size should produce more bytes
        assert len(large) > len(small)

    def test_generate_qr_code_minimum_border(self):
        """Test that border=1 is accepted (our minimum)."""
        result = generate_qr_code("https://example.com/test", border=1)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_generate_qr_code_long_url(self):
        """Test QR code generation with a very long URL."""
        long_url = "https://example.com/" + "a" * 500
        result = generate_qr_code(long_url)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"


def _mock_short_url(short_code="qr_test"):
    """Create a mock short URL for QR code tests."""
    url = MagicMock(spec=ShortURL)
    url.id = "607f1f77bcf86cd799439099"
    url.original_url = "https://example.com/long/url"
    url.short_code = short_code
    url.clicks = 0
    url.is_active = True
    url.expiration = None
    url.created_at = datetime.now(UTC)
    url.user = MagicMock()
    url.user.ref = MagicMock()
    return url


class TestQRCodeEndpoint:
    """Tests for the QR code API endpoint."""

    @pytest.mark.asyncio
    async def test_get_qr_code_success(self):
        """Test successful QR code generation via endpoint."""
        mock_url = _mock_short_url("abc123x")

        with patch("app.api.urls.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/urls/abc123x/qr")

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"
            # Verify it's a valid PNG
            assert response.content[:4] == b"\x89PNG"

    @pytest.mark.asyncio
    async def test_get_qr_code_not_found(self):
        """Test QR code for non-existent URL returns 404."""
        with patch("app.api.urls.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/urls/nonexist/qr")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_qr_code_inactive_url(self):
        """Test QR code for inactive (deleted) URL returns 404."""
        mock_url = _mock_short_url("deleted1")
        mock_url.is_active = False

        with patch("app.api.urls.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/urls/deleted1/qr")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_qr_code_custom_size(self):
        """Test QR code with custom size parameter."""
        mock_url = _mock_short_url("sized01")

        with patch("app.api.urls.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/urls/sized01/qr?size=20&border=2")

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/png"

    @pytest.mark.asyncio
    async def test_get_qr_code_invalid_size_too_large(self):
        """Test QR code with size exceeding maximum."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/urls/abc123x/qr?size=100")

        # FastAPI validation should reject size > 40
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_qr_code_invalid_size_too_small(self):
        """Test QR code with size below minimum."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/urls/abc123x/qr?size=1")

        # FastAPI validation should reject size < 5
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_qr_code_no_auth_required(self):
        """Test that QR code endpoint does not require authentication."""
        mock_url = _mock_short_url("public1")

        with patch("app.api.urls.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # No Authorization header
                response = await client.get("/api/v1/urls/public1/qr")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_qr_code_content_disposition_header(self):
        """Test that the response includes proper content-disposition header."""
        mock_url = _mock_short_url("hdr_tst")

        with patch("app.api.urls.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/urls/hdr_tst/qr")

            assert response.status_code == 200
            assert "hdr_tst-qr.png" in response.headers.get("content-disposition", "")
