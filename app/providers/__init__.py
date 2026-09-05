"""Provider abstraction layer for FraudShield AI.

This module provides a factory for creating LLM and pattern matching providers
based on environment configuration. Providers can be swapped without code changes.

Configuration:
    LLM_PROVIDER: azure_openai | openai | ollama | mock (default: mock)
    PATTERN_PROVIDER: azure_search | local_json | mock (default: local_json)
"""

import os
from typing import Tuple

from app.providers.llm.base import LLMProvider
from app.providers.patterns.base import PatternMatcher


def get_providers() -> Tuple[LLMProvider, PatternMatcher]:
    """Factory function to get configured providers.

    Returns:
        Tuple of (LLMProvider, PatternMatcher) based on environment configuration.
    """
    llm_provider = _get_llm_provider()
    pattern_provider = _get_pattern_provider()
    return llm_provider, pattern_provider


def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider."""
    return _get_llm_provider()


def get_pattern_provider() -> PatternMatcher:
    """Get the configured pattern matching provider."""
    return _get_pattern_provider()


def _get_llm_provider() -> LLMProvider:
    """Create LLM provider based on LLM_PROVIDER environment variable."""
    provider_name = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider_name == "azure_openai":
        from app.providers.llm.azure_openai import AzureOpenAIProvider
        return AzureOpenAIProvider()

    elif provider_name == "openai":
        from app.providers.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()

    elif provider_name == "ollama":
        from app.providers.llm.ollama_provider import OllamaProvider
        return OllamaProvider()

    else:  # mock (default)
        from app.providers.llm.mock_provider import MockLLMProvider
        return MockLLMProvider()


def _get_pattern_provider() -> PatternMatcher:
    """Create pattern provider based on PATTERN_PROVIDER environment variable."""
    provider_name = os.getenv("PATTERN_PROVIDER", "local_json").lower()

    if provider_name == "azure_search":
        from app.providers.patterns.azure_search import AzureSearchProvider
        return AzureSearchProvider()

    elif provider_name == "local_json":
        from app.providers.patterns.local_json import LocalJSONProvider
        return LocalJSONProvider()

    else:  # mock
        from app.providers.patterns.mock_provider import MockPatternProvider
        return MockPatternProvider()
