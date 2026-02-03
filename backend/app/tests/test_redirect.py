"""Tests for redirect service and click tracking."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.url import ShortURL
from app.services.click import parse_user_agent


@pytest.fixture
def mock_short_url():
    """Create a mock short URL for testing."""
    url = MagicMock(spec=ShortURL)
    url.id = "607f1f77bcf86cd799439022"
    url.original_url = "https://example.com/destination"
    url.short_code = "abc123x"
    url.clicks = 5
    url.is_active = True
    url.expiration = None
    url.created_at = datetime.now(UTC)
    url.preview_title = "Example Site"
    url.preview_description = "Example description"
    url.preview_image = "https://example.com/image.png"
    # AI fields
    url.tags = ["example", "test"]
    url.summary = "An example test URL"
    url.suggested_alias = "example-test"
    url.is_toxic = False
    url.ai_analyzed = True
    url.ai_analyzed_at = datetime.now(UTC)
    url.preview_screenshot_id = None
    return url


class TestUserAgentParsing:
    """Tests for user agent parsing."""

    def test_parse_chrome_windows(self):
        """Test parsing Chrome on Windows."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        result = parse_user_agent(ua)
        assert result["browser"] == "Chrome"
        assert result["os"] == "Windows"
        assert result["device_type"] == "desktop"

    def test_parse_safari_mac(self):
        """Test parsing Safari on macOS."""
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"
        result = parse_user_agent(ua)
        assert result["browser"] == "Safari"
        assert result["os"] == "macOS"
        assert result["device_type"] == "desktop"

    def test_parse_mobile_chrome_android(self):
        """Test parsing Chrome on Android mobile."""
        ua = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
        result = parse_user_agent(ua)
        assert result["browser"] == "Chrome"
        assert result["os"] == "Android"
        assert result["device_type"] == "mobile"

    def test_parse_iphone_safari(self):
        """Test parsing Safari on iPhone."""
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"
        result = parse_user_agent(ua)
        assert result["browser"] == "Safari"
        assert result["os"] == "iOS"
        assert result["device_type"] == "mobile"

    def test_parse_ipad(self):
        """Test parsing iPad as tablet."""
        ua = "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"
        result = parse_user_agent(ua)
        assert result["device_type"] == "tablet"
        assert result["os"] == "iOS"

    def test_parse_firefox_linux(self):
        """Test parsing Firefox on Linux."""
        ua = "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
        result = parse_user_agent(ua)
        assert result["browser"] == "Firefox"
        assert result["os"] == "Linux"
        assert result["device_type"] == "desktop"

    def test_parse_edge(self):
        """Test parsing Edge browser."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        result = parse_user_agent(ua)
        assert result["browser"] == "Edge"

    def test_parse_empty_user_agent(self):
        """Test parsing empty user agent."""
        result = parse_user_agent("")
        assert result["device_type"] == "desktop"
        assert result["browser"] == "unknown"
        assert result["os"] == "unknown"

    def test_parse_none_user_agent(self):
        """Test parsing None user agent."""
        result = parse_user_agent(None)
        assert result["device_type"] == "desktop"


class TestRedirectEndpoint:
    """Tests for redirect endpoint."""

    @pytest.mark.asyncio
    async def test_redirect_success(self, mock_short_url):
        """Test successful redirect."""
        with patch("app.api.redirect.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            with patch("app.api.redirect.log_click", new_callable=AsyncMock) as mock_log:
                mock_get.return_value = mock_short_url
                mock_log.return_value = MagicMock()

                transport = ASGITransport(app=app)
                async with AsyncClient(
                    transport=transport, base_url="http://test", follow_redirects=False
                ) as client:
                    response = await client.get("/abc123x")

                assert response.status_code == 302
                assert response.headers["location"] == "https://example.com/destination"

    @pytest.mark.asyncio
    async def test_redirect_not_found(self):
        """Test redirect with non-existent short code."""
        with patch("app.api.redirect.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/nonexistent")

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_redirect_inactive_url(self, mock_short_url):
        """Test redirect with inactive URL."""
        mock_short_url.is_active = False

        with patch("app.api.redirect.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_short_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/abc123x")

            assert response.status_code == 410  # Gone

    @pytest.mark.asyncio
    async def test_redirect_expired_url(self, mock_short_url):
        """Test redirect with expired URL."""
        mock_short_url.expiration = datetime.now(UTC) - timedelta(days=1)

        with patch("app.api.redirect.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_short_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/abc123x")

            assert response.status_code == 410  # Gone

    @pytest.mark.asyncio
    async def test_redirect_with_click_logging(self, mock_short_url):
        """Test that clicks are logged during redirect."""
        with patch("app.api.redirect.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            with patch("app.api.redirect.log_click", new_callable=AsyncMock) as mock_log:
                mock_get.return_value = mock_short_url
                mock_log.return_value = MagicMock()

                transport = ASGITransport(app=app)
                async with AsyncClient(
                    transport=transport, base_url="http://test", follow_redirects=False
                ) as client:
                    response = await client.get(
                        "/abc123x",
                        headers={
                            "User-Agent": "Mozilla/5.0 Chrome/120.0",
                            "Referer": "https://google.com",
                        },
                    )

                assert response.status_code == 302
                mock_log.assert_called_once()


class TestPreviewEndpoint:
    """Tests for URL preview endpoint."""

    @pytest.mark.asyncio
    async def test_preview_success(self, mock_short_url):
        """Test getting URL preview."""
        with patch("app.api.redirect.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_short_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/abc123x/preview")

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Example Site"
            assert data["description"] == "Example description"
            assert data["original_url"] == "https://example.com/destination"

    @pytest.mark.asyncio
    async def test_preview_not_found(self):
        """Test preview for non-existent URL."""
        with patch("app.api.redirect.get_short_url_by_code", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/nonexistent/preview")

            assert response.status_code == 404
