"""Claude API client for LLM interactions."""

import os
from typing import Optional
from anthropic import Anthropic
from dotenv import load_dotenv

from .prompts import PromptTemplates


class ClaudeClient:
    """Client for interacting with Claude API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (if None, reads from env)
            model: Model to use (if None, reads from env or uses default)
            max_tokens: Maximum tokens for response
        """
        load_dotenv()

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it in .env or pass as parameter."
            )

        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        self.max_tokens = max_tokens
        self.client = Anthropic(api_key=self.api_key)

    async def generate_variations_async(
        self,
        strategy_content: str,
        num_variations: int = 3
    ) -> list[str]:
        """
        Generate strategy variations asynchronously.

        Args:
            strategy_content: Original strategy markdown
            num_variations: Number of variations to generate

        Returns:
            List of strategy variation markdown strings
        """
        prompt = PromptTemplates.generate_variations(strategy_content, num_variations)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens * 2,  # Variations need more tokens
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text

        # Split by separator
        variations = response_text.split("---STRATEGY_SEPARATOR---")
        variations = [v.strip() for v in variations if v.strip()]

        return variations

    def generate_variations(
        self,
        strategy_content: str,
        num_variations: int = 3
    ) -> list[str]:
        """
        Generate strategy variations synchronously.

        Args:
            strategy_content: Original strategy markdown
            num_variations: Number of variations to generate

        Returns:
            List of strategy variation markdown strings
        """
        prompt = PromptTemplates.generate_variations(strategy_content, num_variations)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens * 2,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text

        # Split by separator
        variations = response_text.split("---STRATEGY_SEPARATOR---")
        variations = [v.strip() for v in variations if v.strip()]

        return variations

    def strategy_to_code(self, strategy_content: str) -> str:
        """
        Convert strategy markdown to Python code.

        Args:
            strategy_content: Strategy markdown

        Returns:
            Generated Python code
        """
        prompt = PromptTemplates.strategy_to_code(strategy_content)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text

        # Extract code from markdown code blocks if present
        code = self._extract_code(response_text)

        return code

    def validate_code(self, code: str, strategy_name: str) -> tuple[bool, str]:
        """
        Validate generated code.

        Args:
            code: Python code to validate
            strategy_name: Name of the strategy

        Returns:
            Tuple of (is_valid, validated_or_corrected_code)
        """
        prompt = PromptTemplates.validate_code(code, strategy_name)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text.strip()

        if response_text == "VALIDATED":
            return True, code
        else:
            # Extract corrected code
            corrected_code = self._extract_code(response_text)
            return False, corrected_code

    def _extract_code(self, text: str) -> str:
        """Extract Python code from markdown code blocks."""
        # Check for code blocks
        if "```python" in text:
            # Extract content between ```python and ```
            start = text.find("```python") + len("```python")
            end = text.find("```", start)
            code = text[start:end].strip()
            return code
        elif "```" in text:
            # Generic code block
            start = text.find("```") + 3
            end = text.find("```", start)
            code = text[start:end].strip()
            return code
        else:
            # No code block, return as-is
            return text.strip()
