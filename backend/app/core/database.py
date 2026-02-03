import redis.asyncio as redis
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class Database:
    client: AsyncIOMotorClient = None
    redis_client: redis.Redis = None


db = Database()


async def connect_to_mongo():
    """Initialize MongoDB connection with Beanie ODM."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)

    # Import models here to avoid circular imports
    from app.models.click import ClickLog
    from app.models.url import ShortURL
    from app.models.user import User

    await init_beanie(
        database=db.client[settings.MONGODB_DB_NAME], document_models=[User, ShortURL, ClickLog]
    )


async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client:
        db.client.close()


async def connect_to_redis():
    """Initialize Redis connection."""
    db.redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)


async def close_redis_connection():
    """Close Redis connection."""
    if db.redis_client:
        await db.redis_client.close()


def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    return db.redis_client
