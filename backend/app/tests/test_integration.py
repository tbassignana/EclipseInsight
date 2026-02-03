"""Integration tests that exercise full API flows end-to-end (with mocked DB)."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.main import app
from app.models.user import User
from app.models.url import ShortURL
from app.core.security import create_access_token


def _mock_user(email="integration@test.com", is_admin=False):
    user = MagicMock(spec=User)
    user.id = "aaa111bbb222ccc333ddd444"
    user.email = email
    user.hashed_password = "$2b$12$placeholder"
    user.is_active = True
    user.is_admin = is_admin
    user.created_at = datetime.now(timezone.utc)
    user.reset_token = None
    user.reset_token_expires = None
    user.save = AsyncMock()
    user.insert = AsyncMock()
    return user


def _mock_short_url(user, short_code="intTest"):
    url = MagicMock(spec=ShortURL)
    url.id = "bbb222ccc333ddd444eee555"
    url.original_url = "https://example.com/integration"
    url.short_code = short_code
    url.clicks = 5
    url.is_active = True
    url.expiration = None
    url.created_at = datetime.now(timezone.utc)
    url.updated_at = None
    url.custom_alias = None
    url.preview_title = "Example"
    url.preview_description = "Desc"
    url.preview_image = None
    url.user = MagicMock()
    url.user.id = user.id
    url.user.ref = MagicMock()
    url.user.ref.id = user.id
    url.tags = ["test"]
    url.summary = "A test page"
    url.suggested_alias = "test-page"
    url.is_toxic = False
    url.ai_analyzed = True
    url.ai_analyzed_at = datetime.now(timezone.utc)
    url.save = AsyncMock()
    return url


class TestRegisterLoginFlow:
    """Test the full registration → login → authenticated request flow."""

    @pytest.mark.asyncio
    async def test_register_then_login_then_me(self):
        user = _mock_user()

        with (
            patch("app.api.auth.get_user_by_email", new_callable=AsyncMock) as mock_get,
            patch("app.api.auth.create_user", new_callable=AsyncMock) as mock_create,
            patch("app.api.auth.authenticate_user", new_callable=AsyncMock) as mock_auth,
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
        ):
            # Step 1: Register
            mock_get.return_value = None
            mock_create.return_value = user

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                reg = await client.post(
                    "/api/v1/auth/register",
                    json={"email": "integration@test.com", "password": "securepass123"},
                )
            assert reg.status_code == 201

            # Step 2: Login
            mock_auth.return_value = user
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                login = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "integration@test.com", "password": "securepass123"},
                )
            assert login.status_code == 200
            token = login.json()["access_token"]

            # Step 3: /me with real token
            mock_find.return_value = user
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                me = await client.get(
                    "/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert me.status_code == 200
            assert me.json()["email"] == "integration@test.com"


class TestShortenAndStatsFlow:
    """Test shorten → list → stats → edit → delete flow."""

    @pytest.mark.asyncio
    async def test_full_url_lifecycle(self):
        user = _mock_user()
        short = _mock_short_url(user)
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})
        transport = ASGITransport(app=app)

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
            patch("app.api.urls.create_short_url", new_callable=AsyncMock) as mock_create,
            patch("app.api.urls.get_user_urls", new_callable=AsyncMock) as mock_list,
            patch("app.api.urls.get_short_url_by_code", new_callable=AsyncMock) as mock_get,
            patch("app.api.urls.get_url_stats", new_callable=AsyncMock) as mock_stats,
            patch("app.api.urls.update_short_url", new_callable=AsyncMock) as mock_update,
            patch("app.api.urls.delete_short_url", new_callable=AsyncMock) as mock_delete,
        ):
            mock_find.return_value = user

            # Step 1: Shorten
            mock_create.return_value = short
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/urls/shorten",
                    json={"original_url": "https://example.com/integration"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert res.status_code == 201
            assert res.json()["short_code"] == "intTest"

            # Step 2: List
            mock_list.return_value = [short]
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get(
                    "/api/v1/urls",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert res.status_code == 200
            assert len(res.json()) == 1

            # Step 3: Get details
            mock_get.return_value = short
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get(
                    "/api/v1/urls/intTest",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert res.status_code == 200
            assert res.json()["ai"]["tags"] == ["test"]

            # Step 4: Stats
            from app.schemas.url import URLStats
            mock_stats.return_value = URLStats(
                short_code="intTest",
                original_url="https://example.com/integration",
                total_clicks=5,
                clicks_today=2,
                clicks_this_week=4,
                top_referrers=[],
                clicks_by_country=[],
                clicks_by_device=[],
                clicks_over_time=[],
            )
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get(
                    "/api/v1/urls/intTest/stats",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert res.status_code == 200
            assert res.json()["total_clicks"] == 5

            # Step 5: Update (PATCH)
            updated_short = _mock_short_url(user, "intTest")
            updated_short.original_url = "https://updated.com"
            mock_update.return_value = updated_short
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.patch(
                    "/api/v1/urls/intTest",
                    json={"original_url": "https://updated.com"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert res.status_code == 200
            assert res.json()["original_url"] == "https://updated.com"

            # Step 6: Delete
            mock_delete.return_value = True
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.delete(
                    "/api/v1/urls/intTest",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert res.status_code == 200


class TestPasswordResetFlow:
    """Test the full forgot-password → reset flow."""

    @pytest.mark.asyncio
    async def test_forgot_then_reset(self):
        user = _mock_user()
        transport = ASGITransport(app=app)

        with (
            patch("app.services.auth.get_user_by_email", new_callable=AsyncMock) as mock_get,
            patch("app.services.auth.User.find_one", new_callable=AsyncMock) as mock_find_token,
        ):
            # Step 1: Request reset
            mock_get.return_value = user
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/auth/forgot-password",
                    json={"email": "integration@test.com"},
                )
            assert res.status_code == 200
            # Token is saved on the user mock
            assert user.save.called
            token_value = user.reset_token
            assert token_value is not None

            # Step 2: Reset password with token
            user.reset_token_expires = datetime(2099, 1, 1, tzinfo=timezone.utc)
            mock_find_token.return_value = user
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.post(
                    "/api/v1/auth/reset-password",
                    json={"token": token_value, "new_password": "mynewsecure123"},
                )
            assert res.status_code == 200
            assert "successfully" in res.json()["message"]
