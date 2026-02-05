"""Tests for user URL quota feature."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.url import ShortURL
from app.models.user import User
from app.services.url import check_user_url_quota


def _mock_user(is_admin=False):
    user = MagicMock(spec=User)
    user.id = "507f1f77bcf86cd799439011"
    user.email = "quota@example.com"
    user.is_active = True
    user.is_admin = is_admin
    user.created_at = datetime.now(UTC)
    return user


def _mock_short_url(mock_user, short_code="qt_test"):
    url = MagicMock(spec=ShortURL)
    url.id = "607f1f77bcf86cd799439022"
    url.original_url = "https://example.com/quota"
    url.short_code = short_code
    url.clicks = 0
    url.is_active = True
    url.expiration = None
    url.created_at = datetime.now(UTC)
    url.preview_title = None
    url.preview_description = None
    url.preview_image = None
    url.user = MagicMock()
    url.user.id = mock_user.id
    url.user.ref = MagicMock()
    url.user.ref.id = mock_user.id
    url.tags = []
    url.summary = None
    url.suggested_alias = None
    url.is_toxic = False
    url.ai_analyzed = False
    url.ai_analyzed_at = None
    return url


class TestCheckUserUrlQuota:
    """Tests for the quota check service function."""

    @pytest.mark.asyncio
    async def test_quota_not_exceeded(self):
        """Test that no error is raised when under quota."""
        user = _mock_user()

        with (
            patch("app.services.url.settings") as mock_settings,
            patch.object(ShortURL, "find", return_value=MagicMock()) as mock_find,
        ):
            mock_settings.MAX_URLS_PER_USER = 500
            mock_find.return_value.count = AsyncMock(return_value=10)

            # Should not raise
            await check_user_url_quota(user)

    @pytest.mark.asyncio
    async def test_quota_exceeded(self):
        """Test that ValueError is raised when quota is exceeded."""
        user = _mock_user()

        with (
            patch("app.services.url.settings") as mock_settings,
            patch.object(ShortURL, "find", return_value=MagicMock()) as mock_find,
        ):
            mock_settings.MAX_URLS_PER_USER = 100
            mock_find.return_value.count = AsyncMock(return_value=100)

            with pytest.raises(ValueError, match="URL quota exceeded"):
                await check_user_url_quota(user)

    @pytest.mark.asyncio
    async def test_quota_at_limit(self):
        """Test that quota is exceeded at exactly the limit."""
        user = _mock_user()

        with (
            patch("app.services.url.settings") as mock_settings,
            patch.object(ShortURL, "find", return_value=MagicMock()) as mock_find,
        ):
            mock_settings.MAX_URLS_PER_USER = 50
            mock_find.return_value.count = AsyncMock(return_value=50)

            with pytest.raises(ValueError, match="URL quota exceeded"):
                await check_user_url_quota(user)

    @pytest.mark.asyncio
    async def test_admin_bypasses_quota(self):
        """Test that admin users bypass the quota check."""
        admin = _mock_user(is_admin=True)

        with patch("app.services.url.settings") as mock_settings:
            mock_settings.MAX_URLS_PER_USER = 1

            # Should not raise even though limit is 1
            await check_user_url_quota(admin)

    @pytest.mark.asyncio
    async def test_unlimited_quota_zero(self):
        """Test that MAX_URLS_PER_USER=0 means unlimited."""
        user = _mock_user()

        with patch("app.services.url.settings") as mock_settings:
            mock_settings.MAX_URLS_PER_USER = 0

            # Should not raise
            await check_user_url_quota(user)

    @pytest.mark.asyncio
    async def test_quota_one_below_limit(self):
        """Test that being one below quota allows creation."""
        user = _mock_user()

        with (
            patch("app.services.url.settings") as mock_settings,
            patch.object(ShortURL, "find", return_value=MagicMock()) as mock_find,
        ):
            mock_settings.MAX_URLS_PER_USER = 100
            mock_find.return_value.count = AsyncMock(return_value=99)

            # Should not raise
            await check_user_url_quota(user)


class TestQuotaEndpointIntegration:
    """Tests for quota enforcement at the API endpoint level."""

    @pytest.mark.asyncio
    async def test_shorten_blocked_by_quota(self):
        """Test that URL shortening is blocked when quota is exceeded."""
        user = _mock_user()
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
            patch("app.api.urls.create_short_url", new_callable=AsyncMock) as mock_create,
        ):
            mock_find.return_value = user
            mock_create.side_effect = ValueError(
                "URL quota exceeded. You have 500/500 active URLs. "
                "Delete some URLs to create new ones."
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/urls/shorten",
                    json={"original_url": "https://example.com/new"},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 400
            assert "quota exceeded" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_shorten_allowed_under_quota(self):
        """Test that URL shortening works when under quota."""
        user = _mock_user()
        mock_url = _mock_short_url(user, "under01")
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
            patch("app.api.urls.create_short_url", new_callable=AsyncMock) as mock_create,
        ):
            mock_find.return_value = user
            mock_create.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/urls/shorten",
                    json={"original_url": "https://example.com/ok"},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_quota_error_message_includes_count(self):
        """Test that the quota error message includes the count information."""
        user = _mock_user()

        with (
            patch("app.services.url.settings") as mock_settings,
            patch.object(ShortURL, "find", return_value=MagicMock()) as mock_find,
        ):
            mock_settings.MAX_URLS_PER_USER = 200
            mock_find.return_value.count = AsyncMock(return_value=200)

            with pytest.raises(ValueError, match="200/200"):
                await check_user_url_quota(user)


class TestQuotaConfiguration:
    """Tests for quota configuration settings."""

    def test_default_quota_value(self):
        """Test that the default quota is set in config."""
        from app.core.config import Settings

        s = Settings(
            MONGODB_URL="mongodb://test:27017",
            REDIS_URL="redis://test:6379",
        )
        assert s.MAX_URLS_PER_USER == 500

    def test_custom_quota_value(self):
        """Test that quota can be customized."""
        from app.core.config import Settings

        s = Settings(
            MONGODB_URL="mongodb://test:27017",
            REDIS_URL="redis://test:6379",
            MAX_URLS_PER_USER=1000,
        )
        assert s.MAX_URLS_PER_USER == 1000

    def test_quota_zero_means_unlimited(self):
        """Test that quota=0 is valid (unlimited)."""
        from app.core.config import Settings

        s = Settings(
            MONGODB_URL="mongodb://test:27017",
            REDIS_URL="redis://test:6379",
            MAX_URLS_PER_USER=0,
        )
        assert s.MAX_URLS_PER_USER == 0
