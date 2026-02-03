"""
AI Analysis Service using Anthropic Claude API.
Provides content analysis, tagging, summarization, and toxicity detection for URLs.
"""

import json
import re
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup

from app.core.config import settings


@dataclass
class AIAnalysisResult:
    """Result of AI content analysis."""

    tags: list[str]
    summary: str
    suggested_alias: str
    is_toxic: bool
    error: str | None = None


class AnthropicClient:
    """Async client for Anthropic Claude API."""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        self.base_url = "https://api.anthropic.com/v1"

    @property
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    async def analyze_content(self, content: str, url: str) -> AIAnalysisResult:
        """
        Analyze content using Claude to generate tags, summary, alias, and detect toxicity.

        Args:
            content: The text content to analyze
            url: The original URL (used for alias suggestion context)

        Returns:
            AIAnalysisResult with analysis data
        """
        if not self.is_configured:
            return AIAnalysisResult(
                tags=[],
                summary="",
                suggested_alias="",
                is_toxic=False,
                error="ANTHROPIC_API_KEY not configured",
            )

        prompt = f"""Analyze the following web content and provide:
1. Exactly 5 relevant tags (single words or short phrases)
2. A concise 1-sentence summary (max 150 characters)
3. A suggested URL alias (lowercase, hyphens only, 3-20 chars, based on content theme)
4. Toxicity assessment (is this content harmful, hateful, or inappropriate?)

Content URL: {url}

Content:
{content[:8000]}

Respond ONLY with valid JSON in this exact format:
{{
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "summary": "Brief summary of the content",
    "suggested_alias": "content-theme",
    "is_toxic": false
}}"""

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
                payload = {
                    "model": self.model,
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}],
                }

                async with session.post(
                    f"{self.base_url}/messages", headers=headers, json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return AIAnalysisResult(
                            tags=[],
                            summary="",
                            suggested_alias="",
                            is_toxic=False,
                            error=f"API error: {response.status} - {error_text}",
                        )

                    data = await response.json()
                    response_text = data["content"][0]["text"]

                    # Parse JSON response
                    result = json.loads(response_text)

                    # Validate and sanitize alias
                    alias = result.get("suggested_alias", "")
                    alias = re.sub(r"[^a-z0-9-]", "", alias.lower())[:20]

                    return AIAnalysisResult(
                        tags=result.get("tags", [])[:5],
                        summary=result.get("summary", "")[:150],
                        suggested_alias=alias,
                        is_toxic=result.get("is_toxic", False),
                    )

        except json.JSONDecodeError as e:
            return AIAnalysisResult(
                tags=[],
                summary="",
                suggested_alias="",
                is_toxic=False,
                error=f"Failed to parse AI response: {str(e)}",
            )
        except Exception as e:
            return AIAnalysisResult(
                tags=[],
                summary="",
                suggested_alias="",
                is_toxic=False,
                error=f"AI analysis failed: {str(e)}",
            )


class ContentFetcher:
    """Fetches and extracts text content from URLs."""

    @staticmethod
    async def fetch_content(url: str, max_length: int = 10000) -> tuple[str, str | None]:
        """
        Fetch URL content and extract text.

        Args:
            url: URL to fetch
            max_length: Maximum content length to return

        Returns:
            Tuple of (content, error_message)
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; EclipseInsight/1.0; +https://eclipseinsight.com)"
                }
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        return "", f"Failed to fetch URL: HTTP {response.status}"

                    html = await response.text()
                    soup = BeautifulSoup(html, "lxml")

                    # Remove script and style elements
                    for element in soup(["script", "style", "nav", "footer", "header"]):
                        element.decompose()

                    # Get text content
                    text = soup.get_text(separator=" ", strip=True)

                    # Clean up whitespace
                    text = re.sub(r"\s+", " ", text)

                    return text[:max_length], None

        except aiohttp.ClientError as e:
            return "", f"Network error: {str(e)}"
        except Exception as e:
            return "", f"Failed to fetch content: {str(e)}"


class AIAnalysisService:
    """High-level service for AI-powered URL analysis."""

    def __init__(self):
        self.client = AnthropicClient()
        self.fetcher = ContentFetcher()

    @property
    def is_available(self) -> bool:
        """Check if AI analysis is available (API key configured)."""
        return self.client.is_configured

    async def analyze_url(self, url: str) -> AIAnalysisResult:
        """
        Analyze a URL's content using AI.

        Args:
            url: The URL to analyze

        Returns:
            AIAnalysisResult with analysis data
        """
        if not self.is_available:
            return AIAnalysisResult(
                tags=[],
                summary="",
                suggested_alias="",
                is_toxic=False,
                error="AI analysis not available - API key not configured",
            )

        # Fetch content
        content, fetch_error = await self.fetcher.fetch_content(url)
        if fetch_error:
            return AIAnalysisResult(
                tags=[], summary="", suggested_alias="", is_toxic=False, error=fetch_error
            )

        if not content.strip():
            return AIAnalysisResult(
                tags=[],
                summary="",
                suggested_alias="",
                is_toxic=False,
                error="No content found at URL",
            )

        # Analyze content
        return await self.client.analyze_content(content, url)


# Singleton instance
ai_service = AIAnalysisService()
