import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(log_level)
    # Clear any existing handlers to avoid duplicates
    root.handlers.clear()
    root.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)


def validate_settings() -> None:
    """Validate critical settings on startup and emit warnings."""
    logger = logging.getLogger("app.startup")

    if settings.SECRET_KEY in ("your-secret-key-change-in-production", "your-super-secret-key-change-in-production"):
        logger.warning(
            "SECRET_KEY is set to the default insecure value. "
            "Set a strong random SECRET_KEY environment variable before deploying to production."
        )

    if not settings.ANTHROPIC_API_KEY:
        logger.info(
            "ANTHROPIC_API_KEY is not set. AI content analysis features are disabled."
        )

    if settings.DEBUG:
        logger.warning("DEBUG mode is enabled. Do not use in production.")

    logger.info("Configuration validated. App: %s, Base URL: %s", settings.APP_NAME, settings.BASE_URL)
