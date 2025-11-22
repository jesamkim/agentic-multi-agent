"""
Configuration module for AWS Bedrock integration
"""
import os
from typing import Optional


class Config:
    """Configuration for PDF to Markdown conversion using AWS Bedrock"""

    # AWS Configuration
    AWS_PROFILE: str = "profile2"
    AWS_REGION: str = "us-west-2"

    # Bedrock Model Configuration
    MODEL_ID: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    MODEL_ID_HAIKU: str = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
    MODEL_ID_SONNET: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

    # PDF Processing Configuration
    PDF_DPI: int = 450  # Resolution for PDF to image conversion (balanced for accuracy without exceeding API limits)
    IMAGE_FORMAT: str = "PNG"  # PNG for lossless quality

    # Image Extraction Configuration
    SAVE_PAGE_IMAGES: bool = True  # Save full page images
    EXTRACT_EMBEDDED_IMAGES: bool = True  # Extract images from PDF
    MIN_IMAGE_WIDTH: int = 100  # Minimum image width to extract
    MIN_IMAGE_HEIGHT: int = 100  # Minimum image height to extract
    IMAGES_SUBDIR: str = "images"  # Subdirectory for images
    SAVE_IMAGE_METADATA_JSON: bool = True  # Save image metadata as JSON file

    # API Configuration
    MAX_TOKENS: int = 8192  # Maximum tokens for Claude response (increased for detailed output)
    TEMPERATURE: float = 0.05  # Near-deterministic with slight flexibility for character disambiguation

    # System Prompt for OCR
    SYSTEM_PROMPT: str = """You are an expert OCR system. Convert the image content to clean, well-structured Markdown format.

PRIMARY INSTRUCTIONS - Extract ALL Text Content:
- Extract ALL text from the image, including text visible in diagrams and charts
- Preserve the document structure (headings, lists, tables, etc.)
- Maintain proper formatting and hierarchy
- Convert tables to Markdown table format - DO NOT skip tables even if there's an image showing the same information
- Preserve all text content accurately
- Use proper Markdown syntax for emphasis, bold, italic, etc.

TEXT ACCURACY GUIDELINES:
- Pay extra attention to similar-looking characters (especially in CJK languages like Korean, Chinese, Japanese)
- When uncertain between visually similar characters, choose based on context and semantic meaning
- Verify character recognition by considering the surrounding text and overall context
- Examples of commonly confused characters: 교/고, 율/률, 0/O, 1/l/I

TABLE STRUCTURE GUIDELINES:
- Identify merged cells spanning multiple columns or rows
- Preserve hierarchical relationships in nested headers
- For multi-level headers: use proper row grouping to maintain structure
- Align data cells with their correct column headers, even when cells are merged
- For complex tables with groupings: add extra rows to represent the hierarchy clearly
- When a row spans multiple categories: ensure each data value maps to its correct category

SECONDARY INSTRUCTIONS - Indicate Visual Elements:
For diagrams, charts, photos, or other non-text visual elements (NOT tables):
1. AFTER extracting the text content, also insert: ![Descriptive title](IMAGE_PLACEHOLDER)
2. On the NEXT line, add a detailed HTML comment with metadata:
   <!-- Image Description: [Detailed explanation of what the visual element shows]
   Type: [diagram/chart/flowchart/photo/infographic] (NOT table - tables should be extracted as Markdown)
   Key Elements: [List main visual components] -->

IMPORTANT:
- If there's a table with text AND a diagram showing the same information, extract BOTH the table as Markdown text AND indicate the diagram with IMAGE_PLACEHOLDER
- Images are ADDITIONAL context, not replacements for text content
- Always prioritize text extraction first, then add image references

Example:
| Step | Description |
|------|-------------|
| 01 | Report Reception |
| 02 | Review |
| 03 | Investigation |
| 04 | Resolution |

![Process Flowchart](IMAGE_PLACEHOLDER)
<!-- Image Description: Visual flowchart showing the 4-step process with arrows and decision points
Type: flowchart
Key Elements: Sequential flow with connecting arrows between 4 stages -->

- Do not add any other commentary
- Output only the Markdown content"""

    USER_PROMPT: str = """Convert ALL text and content from this image to Markdown format.

STEP 1 - Extract ALL Text (MANDATORY):
- Extract every table as Markdown table format
- For complex tables: pay attention to merged cells and hierarchical headers
- Ensure each data value aligns with its correct column/row category
- Extract all text, headings, lists
- Be careful with visually similar characters - verify using context
- DO NOT skip any text content

STEP 2 - Indicate Visual Elements (ADDITIONAL):
- For diagrams/charts/flowcharts, add: ![title](IMAGE_PLACEHOLDER)
- Add detailed HTML comment with metadata

CRITICAL: If you see a table AND a flowchart showing similar information, extract BOTH:
1. First: The table in Markdown format (with correct structure and alignment)
2. Then: The flowchart image reference with IMAGE_PLACEHOLDER

Visual elements complement text, they don't replace it."""

    # File Paths
    OUTPUT_DIR: str = "output"
    PDF_DIR: str = "pdf"

    @classmethod
    def get_aws_profile(cls) -> str:
        """Get AWS profile name from environment or default"""
        return os.getenv("AWS_PROFILE", cls.AWS_PROFILE)

    @classmethod
    def get_aws_region(cls) -> str:
        """Get AWS region from environment or default"""
        return os.getenv("AWS_REGION", cls.AWS_REGION)

    @classmethod
    def get_model_id(cls) -> str:
        """Get Bedrock model ID"""
        return os.getenv("BEDROCK_MODEL_ID", cls.MODEL_ID)
