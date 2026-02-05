"""Tests for analytics date range filtering feature."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.click import ClickLog
from app.models.url import ShortURL
from app.models.user import User
from app.services.analytics import get_url_stats


def _mock_user():
    user = MagicMock(spec=User)
    user.id = "507f1f77bcf86cd799439011"
    user.email = "datetest@example.com"
    user.is_active = True
    user.is_admin = False
    user.created_at = datetime.now(UTC)
    return user


def _mock_short_url(short_code="datetest"):
    url = MagicMock(spec=ShortURL)
    url.id = "607f1f77bcf86cd799439022"
    url.original_url = "https://example.com/analytics"
    url.short_code = short_code
    url.clicks = 10
    url.is_active = True
    url.expiration = None
    url.created_at = datetime.now(UTC)
    url.user = MagicMock()
    url.user.ref = MagicMock()
    return url


def _make_click(timestamp, referrer=None, browser=None, country=None, device_type=None):
    """Create a mock click log with a specific timestamp."""
    click = MagicMock(spec=ClickLog)
    click.short_url_id = "607f1f77bcf86cd799439022"
    click.timestamp = timestamp
    click.referrer = referrer
    click.browser = browser
    click.country = country
    click.device_type = device_type
    click.os = None
    return click


class TestDateRangeServiceLayer:
    """Tests for date range filtering in the analytics service."""

    @pytest.mark.asyncio
    async def test_stats_without_date_range(self):
        """Test that stats work normally without date range params."""
        mock_url = _mock_short_url("no_range")
        now = datetime.now(UTC)
        clicks = [_make_click(now - timedelta(hours=i)) for i in range(5)]

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=clicks)

            result = await get_url_stats("no_range")

            assert result is not None
            assert result.total_clicks == 5
            assert result.short_code == "no_range"

    @pytest.mark.asyncio
    async def test_stats_with_date_from_only(self):
        """Test filtering with only date_from specified."""
        mock_url = _mock_short_url("from_only")
        now = datetime.now(UTC)
        clicks = [_make_click(now - timedelta(hours=i)) for i in range(3)]

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=clicks)

            date_from = now - timedelta(days=1)
            result = await get_url_stats("from_only", date_from=date_from)

            assert result is not None
            assert result.total_clicks == 3
            # Verify the query included timestamp filter
            call_args = mock_click_find.call_args[0][0]
            assert "timestamp" in call_args
            assert "$gte" in call_args["timestamp"]

    @pytest.mark.asyncio
    async def test_stats_with_date_to_only(self):
        """Test filtering with only date_to specified."""
        mock_url = _mock_short_url("to_only")
        clicks = [_make_click(datetime(2025, 1, 15, tzinfo=UTC))]

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=clicks)

            date_to = datetime(2025, 1, 31, tzinfo=UTC)
            result = await get_url_stats("to_only", date_to=date_to)

            assert result is not None
            # Verify query has $lte
            call_args = mock_click_find.call_args[0][0]
            assert "timestamp" in call_args
            assert "$lte" in call_args["timestamp"]

    @pytest.mark.asyncio
    async def test_stats_with_full_date_range(self):
        """Test filtering with both date_from and date_to."""
        mock_url = _mock_short_url("full_rng")
        clicks = [
            _make_click(datetime(2025, 1, 10, tzinfo=UTC)),
            _make_click(datetime(2025, 1, 20, tzinfo=UTC)),
        ]

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=clicks)

            date_from = datetime(2025, 1, 1, tzinfo=UTC)
            date_to = datetime(2025, 1, 31, tzinfo=UTC)
            result = await get_url_stats("full_rng", date_from=date_from, date_to=date_to)

            assert result is not None
            assert result.total_clicks == 2
            # Verify query has both $gte and $lte
            call_args = mock_click_find.call_args[0][0]
            assert "$gte" in call_args["timestamp"]
            assert "$lte" in call_args["timestamp"]

    @pytest.mark.asyncio
    async def test_stats_date_range_clicks_over_time_uses_range(self):
        """Test that clicks_over_time series spans the custom date range."""
        mock_url = _mock_short_url("cot_rng")
        clicks = [
            _make_click(datetime(2025, 3, 5, 10, 0, tzinfo=UTC)),
            _make_click(datetime(2025, 3, 7, 14, 0, tzinfo=UTC)),
        ]

        with (
            patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find,
            patch.object(ClickLog, "find", return_value=MagicMock()) as mock_click_find,
        ):
            mock_find.return_value = mock_url
            mock_click_find.return_value.to_list = AsyncMock(return_value=clicks)

            date_from = datetime(2025, 3, 1, tzinfo=UTC)
            date_to = datetime(2025, 3, 10, tzinfo=UTC)
            result = await get_url_stats("cot_rng", date_from=date_from, date_to=date_to)

            # Should have 10 days of data (Mar 1 through Mar 10)
            assert len(result.clicks_over_time) == 10
            assert result.clicks_over_time[0]["date"] == "2025-03-01"
            assert result.clicks_over_time[-1]["date"] == "2025-03-10"

    @pytest.mark.asyncio
    async def test_stats_url_not_found(self):
        """Test stats returns None for non-existent URL."""
        with patch.object(ShortURL, "find_one", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None

            result = await get_url_stats("missing")
            assert result is None


class TestDateRangeEndpoint:
    """Tests for date range filtering via the analytics API endpoint."""

    @pytest.mark.asyncio
    async def test_stats_endpoint_with_date_params(self):
        """Test the stats endpoint accepts date_from and date_to query params."""
        user = _mock_user()
        mock_url = _mock_short_url("ep_date")
        mock_url.user.ref.id = user.id
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        from app.schemas.url import URLStats

        mock_stats = URLStats(
            short_code="ep_date",
            original_url="https://example.com/analytics",
            total_clicks=3,
            clicks_today=0,
            clicks_this_week=1,
            top_referrers=[],
            clicks_by_country=[],
            clicks_by_device=[],
            clicks_over_time=[],
        )

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
            patch("app.api.analytics.get_url_stats", new_callable=AsyncMock) as mock_get_stats,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = mock_url
            mock_get_stats.return_value = mock_stats

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/ep_date",
                    params={"date_from": "2025-01-01T00:00:00", "date_to": "2025-01-31T23:59:59"},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["total_clicks"] == 3
            # Verify stats function was called with date params
            mock_get_stats.assert_called_once()
            call_kwargs = mock_get_stats.call_args
            assert call_kwargs.kwargs.get("date_from") is not None
            assert call_kwargs.kwargs.get("date_to") is not None

    @pytest.mark.asyncio
    async def test_stats_endpoint_without_date_params(self):
        """Test the stats endpoint works without date params (backwards compatible)."""
        user = _mock_user()
        mock_url = _mock_short_url("no_date")
        mock_url.user.ref.id = user.id
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        from app.schemas.url import URLStats

        mock_stats = URLStats(
            short_code="no_date",
            original_url="https://example.com/analytics",
            total_clicks=5,
            clicks_today=1,
            clicks_this_week=3,
            top_referrers=[],
            clicks_by_country=[],
            clicks_by_device=[],
            clicks_over_time=[],
        )

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
            patch("app.api.analytics.get_url_stats", new_callable=AsyncMock) as mock_get_stats,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = mock_url
            mock_get_stats.return_value = mock_stats

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/no_date",
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            # Should be called with None date params
            mock_get_stats.assert_called_once_with("no_date", date_from=None, date_to=None)

    @pytest.mark.asyncio
    async def test_stats_endpoint_invalid_date_range(self):
        """Test that date_from > date_to returns 400."""
        user = _mock_user()
        mock_url = _mock_short_url("bad_rng")
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
                    "/api/v1/stats/bad_rng",
                    params={
                        "date_from": "2025-06-01T00:00:00",
                        "date_to": "2025-01-01T00:00:00",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 400
            assert "date_from" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_stats_endpoint_date_from_only(self):
        """Test providing only date_from without date_to."""
        user = _mock_user()
        mock_url = _mock_short_url("from_ep")
        mock_url.user.ref.id = user.id
        token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})

        from app.schemas.url import URLStats

        mock_stats = URLStats(
            short_code="from_ep",
            original_url="https://example.com/analytics",
            total_clicks=2,
            clicks_today=0,
            clicks_this_week=0,
            top_referrers=[],
            clicks_by_country=[],
            clicks_by_device=[],
            clicks_over_time=[],
        )

        with (
            patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find_user,
            patch(
                "app.api.analytics.get_short_url_by_code", new_callable=AsyncMock
            ) as mock_get_url,
            patch("app.api.analytics.get_url_stats", new_callable=AsyncMock) as mock_get_stats,
        ):
            mock_find_user.return_value = user
            mock_get_url.return_value = mock_url
            mock_get_stats.return_value = mock_stats

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/stats/from_ep",
                    params={"date_from": "2025-01-01T00:00:00"},
                    headers={"Authorization": f"Bearer {token}"},
                )

            assert response.status_code == 200
            call_kwargs = mock_get_stats.call_args
            assert call_kwargs.kwargs.get("date_from") is not None
            assert call_kwargs.kwargs.get("date_to") is None
