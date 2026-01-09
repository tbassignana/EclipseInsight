"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from app.main import app
from app.models.user import User
from app.core.security import create_access_token


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = MagicMock(spec=User)
    user.id = "507f1f77bcf86cd799439011"
    user.email = "test@example.com"
    user.hashed_password = "$2b$12$fake.hashed.password"  # Pre-computed hash placeholder
    user.is_active = True
    user.is_admin = False
    user.created_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def auth_token(mock_user):
    """Create a valid JWT token for testing."""
    return create_access_token(data={"sub": mock_user.email, "user_id": str(mock_user.id)})


class TestAuthEndpoints:
    """Tests for authentication API endpoints."""

    @pytest.mark.asyncio
    async def test_register_success(self):
        """Test successful user registration."""
        with patch('app.api.auth.get_user_by_email', new_callable=AsyncMock) as mock_get:
            with patch('app.api.auth.create_user', new_callable=AsyncMock) as mock_create:
                mock_get.return_value = None
                mock_created_user = MagicMock()
                mock_created_user.id = "507f1f77bcf86cd799439011"
                mock_created_user.email = "newuser@example.com"
                mock_created_user.is_active = True
                mock_created_user.is_admin = False
                mock_created_user.created_at = datetime.now(timezone.utc)
                mock_create.return_value = mock_created_user

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/auth/register",
                        json={"email": "newuser@example.com", "password": "testpassword123"}
                    )

                assert response.status_code == 201
                data = response.json()
                assert data["email"] == "newuser@example.com"
                assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        """Test registration with existing email."""
        with patch('app.api.auth.get_user_by_email', new_callable=AsyncMock) as mock_get:
            mock_existing_user = MagicMock()
            mock_existing_user.email = "existing@example.com"
            mock_get.return_value = mock_existing_user

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/register",
                    json={"email": "existing@example.com", "password": "testpassword123"}
                )

            assert response.status_code == 400
            assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self):
        """Test registration with invalid email format."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={"email": "invalid-email", "password": "testpassword123"}
            )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self):
        """Test registration with password too short."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={"email": "test@example.com", "password": "short"}
            )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_success(self, mock_user):
        """Test successful login."""
        with patch('app.api.auth.authenticate_user', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_user

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "test@example.com", "password": "testpassword123"}
                )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Test login with wrong password."""
        with patch('app.api.auth.authenticate_user', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = None

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "test@example.com", "password": "wrongpassword"}
                )

            assert response.status_code == 401
            assert "Incorrect" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, mock_user):
        """Test login with inactive user account."""
        mock_user.is_active = False

        with patch('app.api.auth.authenticate_user', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_user

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "test@example.com", "password": "testpassword123"}
                )

            assert response.status_code == 403
            assert "Inactive" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_me_success(self, mock_user, auth_token):
        """Test getting current user info with valid token."""
        with patch('app.core.security.User.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_user

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == mock_user.email

    @pytest.mark.asyncio
    async def test_get_me_no_token(self):
        """Test getting current user info without token."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self):
        """Test getting current user info with invalid token."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer invalid_token"}
            )

        assert response.status_code == 401


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    def test_password_hash_verify(self):
        """Test that password hashing and verification works."""
        from app.core.security import get_password_hash, verify_password

        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)


class TestJWTTokens:
    """Tests for JWT token utilities."""

    def test_create_and_decode_token(self):
        """Test JWT token creation and decoding."""
        from app.core.security import create_access_token, decode_access_token

        test_data = {"sub": "test@example.com", "user_id": "12345"}
        token = create_access_token(data=test_data)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == test_data["sub"]
        assert decoded["user_id"] == test_data["user_id"]

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        from app.core.security import decode_access_token

        decoded = decode_access_token("invalid_token_string")
        assert decoded is None
