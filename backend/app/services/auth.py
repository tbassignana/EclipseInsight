from datetime import datetime, timezone
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password


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
