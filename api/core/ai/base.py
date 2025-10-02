"""Base class for AI providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum


class AIModel(str, Enum):
    """Supported AI models."""
    GPT4 = "gpt-4"
    GPT4O = "gpt-4o"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    GEMINI_PRO = "gemini-pro"


class AIProvider(ABC):
    """Abstract base class for AI providers.

    Different providers (OpenAI, Anthropic, Google) implement this interface.
    Makes it easy to switch between providers or use multiple providers.
    """

    provider_name: str = "UNKNOWN"
    supported_models: List[AIModel] = []

    def __init__(self, api_key: str, model: str = None):
        """Initialize AI provider.

        Args:
            api_key: API key for the provider
            model: Model to use (defaults to first supported model)
        """
        self.api_key = api_key
        self.model = model or (self.supported_models[0] if self.supported_models else None)

    @abstractmethod
    def process_text(
        self,
        text: str,
        prompt_template: str,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ) -> str:
        """Process text using AI model.

        Args:
            text: Input text to process
            prompt_template: Prompt template with {text} placeholder
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            AI-generated response text
        """
        pass

    @abstractmethod
    def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        examples: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Extract structured data from text.

        Args:
            text: Input text
            schema: JSON schema defining expected output structure
            examples: Optional few-shot examples

        Returns:
            Structured data matching the schema
        """
        pass

    def validate_model(self, model: str) -> bool:
        """Check if model is supported by this provider.

        Args:
            model: Model name to validate

        Returns:
            True if model is supported
        """
        return model in [m.value for m in self.supported_models]

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pass


class AIProviderRegistry:
    """Registry for AI providers.

    Allows dynamic selection of AI provider based on configuration.
    """

    def __init__(self):
        self._providers: Dict[str, type] = {}
        self._instances: Dict[str, AIProvider] = {}

    def register(self, name: str, provider_class: type):
        """Register an AI provider class.

        Args:
            name: Provider name (e.g., 'openai', 'anthropic')
            provider_class: AIProvider subclass
        """
        self._providers[name] = provider_class

    def get_provider(self, name: str, api_key: str, model: str = None) -> AIProvider:
        """Get or create provider instance.

        Args:
            name: Provider name
            api_key: API key
            model: Optional model override

        Returns:
            AIProvider instance

        Raises:
            ValueError: If provider not registered
        """
        cache_key = f"{name}:{model or 'default'}"

        if cache_key not in self._instances:
            if name not in self._providers:
                raise ValueError(f"Provider '{name}' not registered")

            provider_class = self._providers[name]
            self._instances[cache_key] = provider_class(api_key=api_key, model=model)

        return self._instances[cache_key]

    def list_providers(self) -> List[str]:
        """List all registered provider names.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())


# Global registry instance
registry = AIProviderRegistry()
