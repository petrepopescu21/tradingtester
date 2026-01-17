"""Parser for trading strategy markdown files."""

import re
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class ParsedStrategy(BaseModel):
    """Represents a parsed trading strategy."""

    name: str = Field(..., description="Strategy name")
    description: Optional[str] = Field(None, description="Strategy description")
    entry_rules: str = Field(..., description="Entry rules in natural language")
    exit_rules: str = Field(..., description="Exit rules in natural language")
    position_sizing: str = Field(..., description="Position sizing rules")
    risk_management: str = Field(..., description="Risk management parameters")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    raw_content: str = Field(..., description="Raw markdown content")


class StrategyParser:
    """Parse trading strategies from markdown format."""

    REQUIRED_SECTIONS = ["Entry Rules", "Exit Rules", "Position Sizing", "Risk Management"]

    def __init__(self):
        self.section_pattern = re.compile(r'^## (.+)$', re.MULTILINE)
        self.title_pattern = re.compile(r'^# (.+)$', re.MULTILINE)

    def parse_file(self, file_path: str | Path) -> ParsedStrategy:
        """
        Parse a strategy from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            ParsedStrategy object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required sections are missing
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Strategy file not found: {file_path}")

        content = file_path.read_text(encoding='utf-8')
        return self.parse(content)

    def parse(self, content: str) -> ParsedStrategy:
        """
        Parse a strategy from markdown content.

        Args:
            content: Markdown content

        Returns:
            ParsedStrategy object

        Raises:
            ValueError: If required sections are missing
        """
        # Extract title (first H1)
        title_match = self.title_pattern.search(content)
        if not title_match:
            raise ValueError("Strategy must have a title (# heading)")

        name = title_match.group(1).strip()

        # Extract sections
        sections = self._extract_sections(content)

        # Validate required sections
        missing_sections = [s for s in self.REQUIRED_SECTIONS if s not in sections]
        if missing_sections:
            raise ValueError(f"Missing required sections: {', '.join(missing_sections)}")

        # Extract description (content between title and first section)
        description = self._extract_description(content)

        return ParsedStrategy(
            name=name,
            description=description,
            entry_rules=sections["Entry Rules"].strip(),
            exit_rules=sections["Exit Rules"].strip(),
            position_sizing=sections["Position Sizing"].strip(),
            risk_management=sections["Risk Management"].strip(),
            metadata=self._extract_metadata(sections),
            raw_content=content
        )

    def _extract_sections(self, content: str) -> dict[str, str]:
        """Extract all H2 sections from the content."""
        sections = {}
        matches = list(self.section_pattern.finditer(content))

        for i, match in enumerate(matches):
            section_name = match.group(1).strip()
            start = match.end()

            # Find the end of this section (start of next section or end of document)
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = len(content)

            section_content = content[start:end].strip()
            sections[section_name] = section_content

        return sections

    def _extract_description(self, content: str) -> Optional[str]:
        """Extract description between title and first section."""
        title_match = self.title_pattern.search(content)
        if not title_match:
            return None

        start = title_match.end()

        # Find first H2 section
        section_match = self.section_pattern.search(content, start)
        if section_match:
            end = section_match.start()
        else:
            end = len(content)

        description = content[start:end].strip()
        return description if description else None

    def _extract_metadata(self, sections: dict[str, str]) -> dict:
        """Extract any additional metadata from optional sections."""
        metadata = {}

        # Any sections beyond the required ones are stored as metadata
        for section_name, section_content in sections.items():
            if section_name not in self.REQUIRED_SECTIONS:
                metadata[section_name] = section_content

        return metadata

    def validate(self, strategy: ParsedStrategy) -> tuple[bool, list[str]]:
        """
        Validate a parsed strategy.

        Args:
            strategy: ParsedStrategy to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not strategy.name:
            errors.append("Strategy name is required")

        if not strategy.entry_rules:
            errors.append("Entry rules are required")

        if not strategy.exit_rules:
            errors.append("Exit rules are required")

        if not strategy.position_sizing:
            errors.append("Position sizing rules are required")

        if not strategy.risk_management:
            errors.append("Risk management is required")

        return len(errors) == 0, errors
