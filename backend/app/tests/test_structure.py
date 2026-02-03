"""Test that the project structure is set up correctly."""

import os


class TestProjectStructure:
    """Tests for verifying project structure."""

    def test_backend_directories_exist(self):
        """Verify backend directories are created."""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        expected_dirs = [
            "app",
            "app/api",
            "app/models",
            "app/schemas",
            "app/services",
            "app/core",
            "app/tests",
        ]

        for dir_name in expected_dirs:
            dir_path = os.path.join(base_path, dir_name)
            assert os.path.isdir(dir_path), f"Directory {dir_name} should exist"

    def test_core_config_exists(self):
        """Verify core configuration file exists."""
        from app.core.config import settings

        assert settings.APP_NAME == "EclipseInsight"
        assert settings.API_V1_STR == "/api/v1"
        assert settings.SHORT_CODE_LENGTH == 7

    def test_models_importable(self):
        """Verify models can be imported."""
        from app.models.click import ClickLog
        from app.models.url import ShortURL
        from app.models.user import User

        assert User is not None
        assert ShortURL is not None
        assert ClickLog is not None

    def test_schemas_importable(self):
        """Verify schemas can be imported."""
        from app.schemas.url import URLCreate
        from app.schemas.user import UserCreate

        assert UserCreate is not None
        assert URLCreate is not None

    def test_main_app_importable(self):
        """Verify main FastAPI app can be imported."""
        from app.main import app

        assert app is not None
        assert app.title == "EclipseInsight"
