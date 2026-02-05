"""Tests for click analytics CSV export feature."""

import csv
import io
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.click import ClickLog
from app.models.url import ShortURL
from app.models.user import User
from app.services.analytics import export_clicks_csv


def _mock_user():
    user = MagicMock(spec=User)
    user.id = "507f1f77bcf86cd799439011"
    user.email = "csvtest@example.com"
    user.is_active = True
    user.is_admin = False
    user.created_at = datetime.now(UTC)
    return user


def _mock_short_url(short_code="csv_test"):
    url = MagicMock(spec=ShortURL)
    url.id = "607f1f77bcf86cd799439033"
    url.original_url = "https://example.com/export"
    url.short_code = short_code
    url.clicks = 3
    url.is_active = True
    url.expiration = None
    url.created_at = datetime.now(UTC)
    url.user = MagicMock()
    url.user.ref = MagicMock()
    return url


def _make_click(timestamp, referrer=None, browser="Chrome", os="Windows", device="desktop",
                country="US", city="New York"):
    click = MagicMock(spec=ClickLog)
    click.short_url_id = "607f1f77bcf86cd799439033"
    click.timestamp = timestamp
    click.referrer = referrer
    click.browser = browser
    click.os = os
    click.device_type = device
    click.country = country
    click.city = city
    return click


class TestCSVExportService:
    """Tests for the CSV export service function."""

    @pytest.mark.asyncio
    async def test_export_csv_basic(self):
        """Test basic CSV export with clicks."""
        mock_url = _mock_short_url("csv_bas")
        now = datetime.now(UTC)
        clicks = [
            _make_click(now, referrer="https://google.com", browser="Chrome"),
            _make_click(now - timedelta(hours=1), browser="Firefox", country="UK"),
        ]

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=clicks)

            result = await export_clicks_csv("csv_bas")

        assert result is not None
        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        # Header + 2 data rows
        assert len(rows) == 3
        assert rows[0] == ["timestamp", "referrer", "browser", "os", "device_type", "country", "city"]
        assert rows[1][2] == "Chrome"
        assert rows[2][2] == "Firefox"

    @pytest.mark.asyncio
    async def test_export_csv_empty_clicks(self):
        """Test CSV export with no clicks returns header only."""
        mock_url = _mock_short_url("csv_emp")

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=[])

            result = await export_clicks_csv("csv_emp")

        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 1  # Header only
        assert rows[0][0] == "timestamp"

    @pytest.mark.asyncio
    async def test_export_csv_url_not_found(self):
        """Test CSV export returns None for non-existent URL."""
        with patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None

            result = await export_clicks_csv("missing")
            assert result is None

    @pytest.mark.asyncio
    async def test_export_csv_with_date_range(self):
        """Test CSV export respects date range filtering."""
        mock_url = _mock_short_url("csv_rng")
        clicks = [_make_click(datetime(2025, 1, 15, tzinfo=UTC))]

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=clicks)

            date_from = datetime(2025, 1, 1, tzinfo=UTC)
            date_to = datetime(2025, 1, 31, tzinfo=UTC)
            result = await export_clicks_csv("csv_rng", date_from=date_from, date_to=date_to)

            assert result is not None
            # Verify the query included timestamp filter
            call_args = mock_click_find.call_args[0][0]
            assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_export_csv_null_fields_handled(self):
        """Test that null/None fields are exported as empty strings."""
        mock_url = _mock_short_url("csv_nul")
        click = _make_click(
            datetime.now(UTC), referrer=None, browser=None, os=None,
            device=None, country=None, city=None
        )

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=[click])

            result = await export_clicks_csv("csv_nul")

        reader = csv.reader(io.StringIO(result))
        rows = list(reader)
        # All fields after timestamp should be empty strings
        data_row = rows[1]
        assert data_row[1] == ""  # referrer
        assert data_row[2] == ""  # browser
        assert data_row[3] == ""  # os
        assert data_row[4] == ""  # device_type
        assert data_row[5] == ""  # country
        assert data_row[6] == ""  # city


class TestCSVExportEndpoint:
    """Tests for the CSV export API endpoint."""

    @pytest.mark.asyncio
    async def test_export_endpoint_success(self):
        """Test successful CSV export via endpoint."""
        user = _mock_user()
        mock_url = _mock_short_url("ep_csv")
        mock_url.user.ref.id = user.id
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        csv_content = "timestamp,referrer,browser,os,device_type,country,city\n2025-01-15T10:00:00,https://google.com,Chrome,Windows,desktop,US,New York\n"

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
            patch(
                "app.api.analytics.export_clicks_csv", new_callable=AsyncMock
            ) as mock_export,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = mock_url
            mock_export.return_value = csv_content

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/ep_csv/export",
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            assert "ep_csv-analytics.csv" in response.headers.get("content-disposition", "")
            assert "timestamp" in response.text

    @pytest.mark.asyncio
    async def test_export_endpoint_not_found(self):
        """Test CSV export for non-existent URL returns 404."""
        user = _mock_user()
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = None

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/missing/export",
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_endpoint_requires_auth(self):
        """Test that CSV export requires authentication."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/stats/abc123x/export")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_export_endpoint_forbidden_for_other_user(self):
        """Test that users cannot export other users' analytics."""
        user = _mock_user()
        mock_url = _mock_short_url("other01")
        mock_url.user.ref.id = "different_user_id_here"
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/other01/export",
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_export_endpoint_with_date_params(self):
        """Test CSV export with date range parameters."""
        user = _mock_user()
        mock_url = _mock_short_url("dt_csv")
        mock_url.user.ref.id = user.id
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
            patch(
                "app.api.analytics.export_clicks_csv", new_callable=AsyncMock
            ) as mock_export,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = mock_url
            mock_export.return_value = "timestamp,referrer,browser,os,device_type,country,city\n"

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/dt_csv/export",
                    params={"date_from": "2025-01-01T00:00:00", "date_to": "2025-01-31T23:59:59"},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            mock_export.assert_called_once()
            call_kwargs = mock_export.call_args
            assert call_kwargs.kwargs.get("date_from") is not None

    @pytest.mark.asyncio
    async def test_export_endpoint_invalid_date_range(self):
        """Test that date_from > date_to returns 400."""
        user = _mock_user()
        mock_url = _mock_short_url("bd_csv")
        mock_url.user.ref.id = user.id
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = mock_url

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/bd_csv/export",
                    params={
                        "date_from": "2025-12-01T00:00:00",
                        "date_to": "2025-01-01T00:00:00",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 400
