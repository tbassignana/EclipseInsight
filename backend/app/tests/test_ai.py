"""Tests for AI analysis service."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from app.services.ai import (
    AIAnalysisResult,
    AnthropicClient,
    ContentFetcher,
    AIAnalysisService
)


class TestAIAnalysisResult:
    """Tests for AIAnalysisResult dataclass."""

    def test_create_result(self):
        result = AIAnalysisResult(
            tags=["tech", "news"],
            summary="A summary",
            suggested_alias="tech-news",
            is_toxic=False
        )
        assert result.tags == ["tech", "news"]
        assert result.summary == "A summary"
        assert result.suggested_alias == "tech-news"
        assert result.is_toxic is False
        assert result.error is None

    def test_create_result_with_error(self):
        result = AIAnalysisResult(
            tags=[],
            summary="",
            suggested_alias="",
            is_toxic=False,
            error="API key not configured"
        )
        assert result.error == "API key not configured"


class TestAnthropicClient:
    """Tests for AnthropicClient."""

    def test_is_configured_without_key(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
            client = AnthropicClient()
            assert client.is_configured is False

    def test_is_configured_with_key(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
            client = AnthropicClient()
            assert client.is_configured is True

    @pytest.mark.asyncio
    async def test_analyze_content_no_key(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
            client = AnthropicClient()
            result = await client.analyze_content("test content", "https://example.com")
            assert result.error == "ANTHROPIC_API_KEY not configured"
            assert result.tags == []

    @pytest.mark.asyncio
    async def test_analyze_content_success(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

            mock_response = {
                "content": [{
                    "text": json.dumps({
                        "tags": ["python", "programming", "tutorial", "coding", "dev"],
                        "summary": "A Python programming tutorial",
                        "suggested_alias": "python-tutorial",
                        "is_toxic": False
                    })
                }]
            }

            with patch("aiohttp.ClientSession") as mock_session:
                mock_resp = AsyncMock()
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=mock_response)

                mock_ctx = AsyncMock()
                mock_ctx.__aenter__.return_value = mock_resp

                mock_session_inst = MagicMock()
                mock_session_inst.post.return_value = mock_ctx
                mock_session_inst.__aenter__ = AsyncMock(return_value=mock_session_inst)
                mock_session_inst.__aexit__ = AsyncMock()

                mock_session.return_value = mock_session_inst

                client = AnthropicClient()
                result = await client.analyze_content("test content", "https://example.com")

                assert result.tags == ["python", "programming", "tutorial", "coding", "dev"]
                assert result.summary == "A Python programming tutorial"
                assert result.suggested_alias == "python-tutorial"
                assert result.is_toxic is False
                assert result.error is None


class TestContentFetcher:
    """Tests for ContentFetcher."""

    @pytest.mark.asyncio
    async def test_fetch_content_success(self):
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Hello World</h1>
                <p>This is test content.</p>
            </body>
        </html>
        """

        with patch("aiohttp.ClientSession") as mock_session:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.text = AsyncMock(return_value=html_content)

            mock_ctx = AsyncMock()
            mock_ctx.__aenter__.return_value = mock_resp

            mock_session_inst = MagicMock()
            mock_session_inst.get.return_value = mock_ctx
            mock_session_inst.__aenter__ = AsyncMock(return_value=mock_session_inst)
            mock_session_inst.__aexit__ = AsyncMock()

            mock_session.return_value = mock_session_inst

            content, error = await ContentFetcher.fetch_content("https://example.com")

            assert "Hello World" in content
            assert "test content" in content
            assert error is None

    @pytest.mark.asyncio
    async def test_fetch_content_404(self):
        with patch("aiohttp.ClientSession") as mock_session:
            mock_resp = AsyncMock()
            mock_resp.status = 404

            mock_ctx = AsyncMock()
            mock_ctx.__aenter__.return_value = mock_resp

            mock_session_inst = MagicMock()
            mock_session_inst.get.return_value = mock_ctx
            mock_session_inst.__aenter__ = AsyncMock(return_value=mock_session_inst)
            mock_session_inst.__aexit__ = AsyncMock()

            mock_session.return_value = mock_session_inst

            content, error = await ContentFetcher.fetch_content("https://example.com")

            assert content == ""
            assert "HTTP 404" in error


class TestAIAnalysisService:
    """Tests for AIAnalysisService high-level service."""

    def test_is_available_without_key(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
            service = AIAnalysisService()
            assert service.is_available is False

    def test_is_available_with_key(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
            service = AIAnalysisService()
            assert service.is_available is True

    @pytest.mark.asyncio
    async def test_analyze_url_no_key(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = None
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
            service = AIAnalysisService()
            result = await service.analyze_url("https://example.com")
            assert "not available" in result.error


class TestAliasValidation:
    """Tests for alias sanitization."""

    @pytest.mark.asyncio
    async def test_alias_sanitization(self):
        with patch("app.services.ai.settings") as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

            # Test with invalid characters in alias
            mock_response = {
                "content": [{
                    "text": json.dumps({
                        "tags": ["test"],
                        "summary": "Test",
                        "suggested_alias": "Test_Alias!@#$%",
                        "is_toxic": False
                    })
                }]
            }

            with patch("aiohttp.ClientSession") as mock_session:
                mock_resp = AsyncMock()
                mock_resp.status = 200
                mock_resp.json = AsyncMock(return_value=mock_response)

                mock_ctx = AsyncMock()
                mock_ctx.__aenter__.return_value = mock_resp

                mock_session_inst = MagicMock()
                mock_session_inst.post.return_value = mock_ctx
                mock_session_inst.__aenter__ = AsyncMock(return_value=mock_session_inst)
                mock_session_inst.__aexit__ = AsyncMock()

                mock_session.return_value = mock_session_inst

                client = AnthropicClient()
                result = await client.analyze_content("test", "https://example.com")

                # Should be sanitized to lowercase with only alphanumeric and hyphens
                assert result.suggested_alias == "testalias"
