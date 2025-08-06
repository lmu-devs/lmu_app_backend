"""
Utilities for handling HTML content and conversions.
"""

import re

from bs4 import Tag
from markdownify import markdownify as md


def html_to_markdown(html_content: Tag | str, **options) -> str:
    """
    Convert HTML content to Markdown while preserving essential formatting.

    Args:
        html_content: HTML string or BeautifulSoup Tag to convert
        **options: Additional options to pass to markdownify
            - heading_style: ATX (###) or SETEXT (---)
            - bullets: String of bullet styles to use (*+-)
            - strip: List of HTML tags to strip out
            - convert: List of HTML tags to convert (exclusive with strip)
            - escape_asterisks: Whether to escape * in text
            - escape_underscores: Whether to escape _ in text
            - newline_style: SPACES or BACKSLASH
            - wrap: Whether to wrap text at wrap_width
            - wrap_width: Character width to wrap at

    Returns:
        str: Converted Markdown text
    """
    default_options = {
        "heading_style": "ATX",  # Use ### style headings
        "bullets": "*+-",  # Alternate between these bullet styles
        "newline_style": "SPACES",  # Use two spaces for line breaks
        "strip": [],  # Don't strip any tags by default
        "escape_asterisks": True,  # Escape * characters
        "escape_underscores": True,  # Escape _ characters
        "wrap": False,  # Disable text wrapping
        "wrap_width": 80,  # Wrap at 80 characters
    }

    # Override defaults with any provided options
    conversion_options = {**default_options, **options}

    # If input is a Tag, convert to string
    if isinstance(html_content, Tag):
        html_content = str(html_content)

    # Convert to markdown
    markdown_text = md(html_content, **conversion_options)

    # Clean up extra whitespace while preserving intentional line breaks
    markdown_text = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown_text)
    markdown_text = markdown_text.strip()

    return markdown_text
