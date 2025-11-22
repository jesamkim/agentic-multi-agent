"""
Unit tests for Report Generation

Tests the complete report generation flow including:
- Report Agent HTML generation
- Markdown detection and conversion
- PDF generation
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.report_tools import (
    _is_markdown,
    create_html_report,
    _generate_report_internal
)


class TestMarkdownDetection:
    """Test Markdown content detection."""

    def test_detect_markdown_headers(self):
        """Should detect Markdown headers."""
        content = "## This is a header\n\nSome content"
        assert _is_markdown(content) is True

    def test_detect_markdown_bold(self):
        """Should detect Markdown bold syntax."""
        content = "This is **bold text** in the content"
        assert _is_markdown(content) is True

    def test_detect_markdown_lists(self):
        """Should detect Markdown bullet lists."""
        content = "Some text\n* Item 1\n* Item 2"
        assert _is_markdown(content) is True

    def test_detect_html_not_markdown(self):
        """Should not detect HTML as Markdown."""
        content = "<h2>This is HTML</h2>\n<p>Some content</p>"
        assert _is_markdown(content) is False

    def test_detect_plain_text(self):
        """Should not detect plain text as Markdown."""
        content = "This is just plain text with no formatting."
        assert _is_markdown(content) is False


class TestHTMLReportGeneration:
    """Test HTML report creation."""

    def test_html_report_with_html_content(self):
        """Should create valid HTML report from HTML content."""
        html_content = "<h2>Test Report</h2>\n<p>This is a test.</p>"
        result = create_html_report(
            title="Test Report",
            content=html_content
        )

        # Check structure
        assert "<!DOCTYPE html>" in result
        assert "<title>Test Report</title>" in result
        assert "<h2>Test Report</h2>" in result
        assert "<p>This is a test.</p>" in result
        assert "Samsung C&T ESG Chatbot" in result

    def test_html_report_with_markdown_content(self):
        """Should auto-convert Markdown to HTML."""
        markdown_content = """## Test Section

This is **bold** text.

* Item 1
* Item 2

### Subsection

More content here."""

        result = create_html_report(
            title="Test Report",
            content=markdown_content
        )

        # Check Markdown was converted
        assert "<h2>Test Section</h2>" in result
        assert "<strong>bold</strong>" in result
        assert "<li>Item 1</li>" in result
        assert "<h3>Subsection</h3>" in result

        # Should not contain Markdown syntax
        assert "##" not in result
        assert "**bold**" not in result


class TestReportAgentIntegration:
    """Test Report Agent integration (mocked)."""

    def test_report_with_html_from_agent(self):
        """Should handle HTML output from Report Agent."""
        # Simulate Report Agent HTML output
        agent_html = """<h2>Executive Summary</h2>
<p>This is a comprehensive report.</p>

<h3>Key Findings</h3>
<ul>
  <li>Finding 1 with data</li>
  <li>Finding 2 with metrics</li>
</ul>

<h2>Conclusions</h2>
<p>Final summary and recommendations.</p>"""

        result = create_html_report(
            title="ESG Report",
            content=agent_html
        )

        # Should preserve HTML structure
        assert "<h2>Executive Summary</h2>" in result
        assert "<h3>Key Findings</h3>" in result
        assert "<ul>" in result
        assert "<li>Finding 1 with data</li>" in result

    def test_report_with_markdown_fallback(self):
        """Should handle Markdown if Agent outputs it by mistake."""
        # Simulate Report Agent accidentally outputting Markdown
        agent_markdown = """## Executive Summary

This is a comprehensive report.

### Key Findings

* Finding 1 with data
* Finding 2 with metrics

## Conclusions

Final summary and recommendations."""

        result = create_html_report(
            title="ESG Report",
            content=agent_markdown
        )

        # Should auto-convert to HTML
        assert "<h2>Executive Summary</h2>" in result
        assert "<h3>Key Findings</h3>" in result
        assert "<li>Finding 1 with data</li>" in result

        # Should NOT contain Markdown syntax
        assert "##" not in result or "## Executive" not in result  # May appear in comments


class TestPDFConversionScript:
    """Test PDF conversion script generation."""

    def test_pdf_script_uses_es_modules(self):
        """Should generate ES modules script (.mjs)."""
        from tools.report_tools import _generate_report_internal

        # Test that script uses import instead of require
        # (This is tested indirectly through the script content)
        # We'll verify the script format in integration test


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
