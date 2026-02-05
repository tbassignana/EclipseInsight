"""Tests for bulk URL delete feature."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.core.security import create_access_token
from app.main import app
from app.models.user import User
from app.schemas.url import BulkDeleteRequest, BulkDeleteResponse


def _mock_user():
    user = MagicMock(spec=User)
    user.id = "507f1f77bcf86cd799439011"
    user.email = "bulktest@example.com"
    user.is_active = True
    user.is_admin = False
    user.created_at = datetime.now(UTC)
    return user


class TestBulkDeleteSchema:
    """Tests for the bulk delete request/response schemas."""

    def test_bulk_delete_request_valid(self):
        """Test valid bulk delete request."""
        req = BulkDeleteRequest(short_codes=["abc123x", "def456y"])
        assert len(req.short_codes) == 2

    def test_bulk_delete_request_empty_list_rejected(self):
        """Test that empty list is rejected by validation."""
        with pytest.raises(ValidationError):
            BulkDeleteRequest(short_codes=[])

    def test_bulk_delete_response(self):
        """Test bulk delete response model."""
        resp = BulkDeleteResponse(
            deleted=["abc123x"],
            failed=["def456y"],
            total_deleted=1,
            total_failed=1,
        )
        assert resp.total_deleted == 1
        assert resp.total_failed == 1
        assert "abc123x" in resp.deleted
        assert "def456y" in resp.failed


class TestBulkDeleteEndpoint:
    """Tests for the bulk delete API endpoint."""

    @pytest.mark.asyncio
    async def test_bulk_delete_all_success(self):
        """Test bulk deleting multiple URLs successfully."""
        user = _mock_user()
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
            patch(
                "app.api.urls.bulk_delete_short_urls", new_callable=AsyncMock
            ) as mock_bulk_del,
        ):
            mock_find.return_value = user
            mock_bulk_del.return_value = (["code1xx", "code2xx"], [])

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/urls/bulk-delete",
                    json={"short_codes": ["code1xx", "code2xx"]},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["total_deleted"] == 2
            assert data["total_failed"] == 0
            assert "code1xx" in data["deleted"]
            assert "code2xx" in data["deleted"]

    @pytest.mark.asyncio
    async def test_bulk_delete_partial_success(self):
        """Test bulk delete with some failures (not found or not owned)."""
        user = _mock_user()
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
            patch(
                "app.api.urls.bulk_delete_short_urls", new_callable=AsyncMock
            ) as mock_bulk_del,
        ):
            mock_find.return_value = user
            mock_bulk_del.return_value = (["code1xx"], ["notfond"])

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/urls/bulk-delete",
                    json={"short_codes": ["code1xx", "notfond"]},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["total_deleted"] == 1
            assert data["total_failed"] == 1
            assert "code1xx" in data["deleted"]
            assert "notfond" in data["failed"]

    @pytest.mark.asyncio
    async def test_bulk_delete_all_fail(self):
        """Test bulk delete when all deletions fail."""
        user = _mock_user()
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
            patch(
                "app.api.urls.bulk_delete_short_urls", new_callable=AsyncMock
            ) as mock_bulk_del,
        ):
            mock_find.return_value = user
            mock_bulk_del.return_value = ([], ["bad1xxx", "bad2xxx"])

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/urls/bulk-delete",
                    json={"short_codes": ["bad1xxx", "bad2xxx"]},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["total_deleted"] == 0
            assert data["total_failed"] == 2

    @pytest.mark.asyncio
    async def test_bulk_delete_requires_auth(self):
        """Test that bulk delete requires authentication."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/urls/bulk-delete",
                json={"short_codes": ["abc123x"]},
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bulk_delete_empty_list_rejected(self):
        """Test that empty short_codes list is rejected by validation."""
        user = _mock_user()
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = user

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/urls/bulk-delete",
                    json={"short_codes": []},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_bulk_delete_single_item(self):
        """Test bulk delete with a single URL works."""
        user = _mock_user()
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find,
            patch(
                "app.api.urls.bulk_delete_short_urls", new_callable=AsyncMock
            ) as mock_bulk_del,
        ):
            mock_find.return_value = user
            mock_bulk_del.return_value = (["single1"], [])

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/urls/bulk-delete",
                    json={"short_codes": ["single1"]},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["total_deleted"] == 1


class TestBulkDeleteServiceLayer:
    """Tests for the bulk delete service function."""

    @pytest.mark.asyncio
    async def test_bulk_delete_service_delegates_to_single_delete(self):
        """Test that bulk_delete_short_urls calls delete_short_url for each code."""
        from app.services.url import bulk_delete_short_urls

        user = _mock_user()

        with patch("app.services.url.delete_short_url", new_callable=AsyncMock) as mock_del:
            mock_del.side_effect = [True, False, True]

            deleted, failed = await bulk_delete_short_urls(
                ["url1xxx", "url2xxx", "url3xxx"], user
            )

            assert deleted == ["url1xxx", "url3xxx"]
            assert failed == ["url2xxx"]
            assert mock_del.call_count == 3

    @pytest.mark.asyncio
    async def test_bulk_delete_service_empty_result(self):
        """Test bulk delete with all failures."""
        from app.services.url import bulk_delete_short_urls

        user = _mock_user()

        with patch("app.services.url.delete_short_url", new_callable=AsyncMock) as mock_del:
            mock_del.return_value = False

            deleted, failed = await bulk_delete_short_urls(["a1b2c3d", "x1y2z3w"], user)

            assert deleted == []
            assert failed == ["a1b2c3d", "x1y2z3w"]
