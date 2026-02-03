import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

RESET_TOKEN_EXPIRE_HOURS = 1


async def get_user_by_email(email: str) -> Optional[User]:
    """Find a user by their email address."""
    return await User.find_one({"email": email})


async def create_user(user_data: UserCreate) -> User:
    """Create a new user with hashed password."""
    hashed_password = get_password_hash(user_data.password)

    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        created_at=datetime.now(timezone.utc)
    )

    await user.insert()
    return user


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_password_reset_token(email: str) -> Optional[str]:
    """Generate a password reset token for the user. Returns the token, or None if user not found."""
    user = await get_user_by_email(email)
    if not user:
        return None

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    await user.save()

    logger.info("Password reset token generated for %s: %s", email, token)
    return token


async def reset_password(token: str, new_password: str) -> bool:
    """Reset a user's password using a valid reset token. Returns True on success."""
    user = await User.find_one({"reset_token": token})
    if not user:
        return False

    if user.reset_token_expires is None or user.reset_token_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return False

    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    return True
