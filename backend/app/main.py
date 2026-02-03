from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import (
    connect_to_mongo,
    close_mongo_connection,
    connect_to_redis,
    close_redis_connection
)
from app.core.logging import setup_logging, validate_settings


# Initialize logging before anything else
setup_logging()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup
    validate_settings()
    await connect_to_mongo()
    await connect_to_redis()
    yield
    # Shutdown
    await close_mongo_connection()
    await close_redis_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="""
## EclipseInsight - AI-Powered URL Shortener

EclipseInsight is an advanced URL shortening service with AI-powered content analysis.

### Features:
- **AI Content Analysis**: Automatically analyze URLs using Claude AI
- **Smart Auto-Tagging**: Generate relevant tags from content
- **AI Summaries**: Get concise content summaries
- **Toxicity Detection**: Automatically reject harmful content
- **Suggested Aliases**: AI-recommended memorable short codes
- **Rich Previews**: Auto-generated Open Graph previews
- **Real-Time Analytics**: Track clicks, referrers, devices, and geography
- **Custom Expiration**: Set link expiration dates
- **Rate Limiting**: Built-in protection against abuse

### Authentication:
All URL creation and management endpoints require Bearer token authentication.
Use `/api/v1/auth/login` to obtain a token.
    """,
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}


# Import and include routers
from app.api import auth, urls, redirect, analytics, admin
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(urls.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
# Redirect router at root level for short URLs
app.include_router(redirect.router)
