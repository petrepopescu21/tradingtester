"""Code generator for converting strategy markdown to Python code."""

import re
from pathlib import Path
from typing import Optional

from backend.llm.client import ClaudeClient
from backend.strategy_parser.parser import ParsedStrategy


class CodeGenerator:
    """Generate executable Python code from strategy markdown."""

    def __init__(self, llm_client: Optional[ClaudeClient] = None):
        """
        Initialize code generator.

        Args:
            llm_client: Claude client instance (creates new one if None)
        """
        self.llm_client = llm_client or ClaudeClient()

    def generate(
        self,
        strategy: ParsedStrategy,
        validate: bool = True
    ) -> tuple[str, str]:
        """
        Generate Python code for a strategy.

        Args:
            strategy: Parsed strategy
            validate: Whether to validate generated code

        Returns:
            Tuple of (class_name, generated_code)
        """
        # Generate code using LLM
        code = self.llm_client.strategy_to_code(strategy.raw_content)

        # Optionally validate and correct
        if validate:
            is_valid, validated_code = self.llm_client.validate_code(
                code,
                strategy.name
            )
            if not is_valid:
                print(f"Code was corrected during validation for {strategy.name}")
                code = validated_code

        # Extract class name
        class_name = self._extract_class_name(code)
        if not class_name:
            # Generate a valid class name from strategy name
            class_name = self._sanitize_class_name(strategy.name)
            # Insert class definition if not present
            code = self._ensure_class_definition(code, class_name)

        # Add imports if not present
        code = self._ensure_imports(code)

        return class_name, code

    def save_to_file(
        self,
        code: str,
        output_path: str | Path,
        overwrite: bool = False
    ):
        """
        Save generated code to a Python file.

        Args:
            code: Python code
            output_path: Path to save file
            overwrite: Whether to overwrite existing file

        Raises:
            FileExistsError: If file exists and overwrite is False
        """
        output_path = Path(output_path)

        if output_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {output_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding='utf-8')

    def _extract_class_name(self, code: str) -> Optional[str]:
        """Extract class name from Python code."""
        match = re.search(r'class\s+(\w+)\s*[\(:]', code)
        return match.group(1) if match else None

    def _sanitize_class_name(self, name: str) -> str:
        """Convert strategy name to valid Python class name."""
        # Remove special characters and spaces
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_'))

        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'Strategy_' + sanitized

        # Convert to PascalCase
        parts = sanitized.split('_')
        class_name = ''.join(word.capitalize() for word in parts if word)

        return class_name or 'GeneratedStrategy'

    def _ensure_class_definition(self, code: str, class_name: str) -> str:
        """Ensure code has proper class definition."""
        if 'class ' not in code:
            # Wrap code in a class definition
            return f"""class {class_name}(Strategy):
    '''Generated trading strategy.'''

{self._indent_code(code, 4)}
"""
        return code

    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces."""
        indent = ' ' * spaces
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)

    def _ensure_imports(self, code: str) -> str:
        """Ensure necessary imports are present."""
        imports = """import pandas as pd
import numpy as np
from backend.code_generator.base_strategy import Strategy

"""
        # Check if imports are already present
        if 'import pandas' not in code:
            code = imports + code

        return code

    def generate_from_file(
        self,
        strategy_file: str | Path,
        output_file: Optional[str | Path] = None,
        validate: bool = True
    ) -> tuple[str, str]:
        """
        Generate code from a strategy markdown file.

        Args:
            strategy_file: Path to strategy markdown file
            output_file: Optional path to save generated code
            validate: Whether to validate generated code

        Returns:
            Tuple of (class_name, generated_code)
        """
        from backend.strategy_parser.parser import StrategyParser

        parser = StrategyParser()
        strategy = parser.parse_file(strategy_file)

        class_name, code = self.generate(strategy, validate=validate)

        if output_file:
            self.save_to_file(code, output_file, overwrite=True)

        return class_name, code
