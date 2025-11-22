"""
PDF to Markdown converter using AWS Bedrock Claude Haiku 4.5
"""
import argparse
import logging
import tempfile
import shutil
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from pdf2image import convert_from_path
from PIL import Image

from config import Config
from bedrock_client import BedrockClient
from image_extractor import ImageExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFToMarkdownConverter:
    """Convert PDF documents to Markdown using Zerox OCR approach with Bedrock"""

    def __init__(
        self,
        profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        model_id: Optional[str] = None
    ):
        """
        Initialize converter

        Args:
            profile_name: AWS profile name
            region_name: AWS region
            model_id: Bedrock model ID
        """
        self.bedrock_client = BedrockClient(
            profile_name=profile_name,
            region_name=region_name,
            model_id=model_id
        )

    def pdf_to_images(
        self,
        pdf_path: str,
        dpi: int = Config.PDF_DPI,
        output_format: str = Config.IMAGE_FORMAT,
        first_page: Optional[int] = None,
        last_page: Optional[int] = None
    ) -> list[str]:
        """
        Convert PDF to images (one per page)

        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for conversion
            output_format: Image format (PNG, JPEG)
            first_page: First page to convert (1-indexed)
            last_page: Last page to convert (1-indexed)

        Returns:
            List of temporary image file paths
        """
        page_range = ""
        if first_page is not None:
            page_range = f" (pages {first_page}"
            if last_page is not None:
                page_range += f"-{last_page}"
            page_range += ")"

        logger.info(f"Converting PDF to images: {pdf_path}{page_range}")
        logger.info(f"Settings - DPI: {dpi}, Format: {output_format}")

        try:
            # Create temporary directory for images
            temp_dir = tempfile.mkdtemp(prefix='pdf2img_')
            logger.info(f"Temporary directory: {temp_dir}")

            # Get page range
            from pdf2image import pdfinfo_from_path
            info = pdfinfo_from_path(pdf_path)
            total_pages = info['Pages']

            if first_page is None:
                first_page = 1
            if last_page is None:
                last_page = total_pages

            # Validate page range
            if first_page < 1 or first_page > total_pages:
                raise ValueError(f"first_page {first_page} is out of range (1-{total_pages})")
            if last_page < first_page or last_page > total_pages:
                raise ValueError(f"last_page {last_page} is out of range ({first_page}-{total_pages})")

            # Convert PDF to images one page at a time (memory efficient)
            image_paths = []
            for page_num in range(first_page, last_page + 1):
                # Convert single page
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    fmt=output_format.lower(),
                    first_page=page_num,
                    last_page=page_num
                )

                # Save image to temporary file
                image_path = Path(temp_dir) / f"page_{page_num:04d}.{output_format.lower()}"
                images[0].save(image_path, output_format)
                image_paths.append(str(image_path))
                logger.info(f"Saved page {page_num}/{last_page}: {image_path}")

            logger.info(f"Successfully converted {len(image_paths)} pages")
            return image_paths

        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise

    def convert_pdf_to_markdown(
        self,
        pdf_path: str,
        output_path: Optional[str] = None,
        dpi: int = Config.PDF_DPI,
        first_page: Optional[int] = None,
        last_page: Optional[int] = None
    ) -> str:
        """
        Convert entire PDF to Markdown with image extraction

        Args:
            pdf_path: Path to PDF file
            output_path: Optional output path for Markdown file
            dpi: Resolution for PDF to image conversion
            first_page: First page to convert (1-indexed)
            last_page: Last page to convert (1-indexed)

        Returns:
            Markdown text
        """
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Starting PDF to Markdown conversion: {pdf_path}")
        logger.info(f"PDF size: {pdf_path_obj.stat().st_size / 1024 / 1024:.2f} MB")

        # Prepare image output directory
        images_dir = None
        if output_path and (Config.SAVE_PAGE_IMAGES or Config.EXTRACT_EMBEDDED_IMAGES):
            output_path_obj = Path(output_path)
            doc_name = output_path_obj.stem
            images_dir = output_path_obj.parent / f"{doc_name}_{Config.IMAGES_SUBDIR}"
            images_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Images will be saved to: {images_dir}")

        temp_dir = None
        image_extractor = None
        all_extracted_images = {}  # page_num -> list of image metadata

        try:
            # Initialize image extractor if needed
            if Config.EXTRACT_EMBEDDED_IMAGES:
                image_extractor = ImageExtractor(pdf_path)

            # Step 1: Convert PDF to images
            image_paths = self.pdf_to_images(pdf_path, dpi=dpi, first_page=first_page, last_page=last_page)
            temp_dir = Path(image_paths[0]).parent

            # Step 2: Save page images and extract embedded images
            page_start = first_page if first_page else 1
            for idx, temp_image_path in enumerate(image_paths):
                page_num = page_start + idx

                # Save page image
                if Config.SAVE_PAGE_IMAGES and images_dir:
                    page_image_filename = f"page_{page_num:03d}.png"
                    page_image_path = images_dir / page_image_filename
                    shutil.copy(temp_image_path, page_image_path)
                    logger.info(f"Saved page {page_num} image: {page_image_filename}")

                # Extract embedded images
                if Config.EXTRACT_EMBEDDED_IMAGES and images_dir and image_extractor:
                    extracted = image_extractor.extract_images_from_page(
                        page_num,
                        str(images_dir),
                        min_width=Config.MIN_IMAGE_WIDTH,
                        min_height=Config.MIN_IMAGE_HEIGHT
                    )
                    if extracted:
                        all_extracted_images[page_num] = extracted
                        logger.info(f"Extracted {len(extracted)} images from page {page_num}")

            # Step 3: Process images through Bedrock with streaming write
            logger.info(f"Processing {len(image_paths)} pages through Bedrock Claude Sonnet 4.5")

            # Write header to output file first
            output_path_obj = None
            if output_path:
                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                self._write_markdown_header(output_path_obj, pdf_path_obj.stem, len(image_paths))
                logger.info(f"Writing Markdown to: {output_path}")

            # Process each page individually with retry logic
            failed_pages = []
            for idx, image_path in enumerate(image_paths, 1):
                page_num = page_start + idx - 1

                # Try processing with retries
                page_markdown = None
                max_retries = 3
                retry_delay = 2  # seconds

                for attempt in range(1, max_retries + 1):
                    try:
                        logger.info(f"Processing page {idx}/{len(image_paths)} ({idx/len(image_paths)*100:.1f}%) - Attempt {attempt}/{max_retries}")
                        page_markdown = self.bedrock_client.image_to_markdown(image_path)

                        # Replace IMAGE_PLACEHOLDER for this page
                        if page_num in all_extracted_images and all_extracted_images[page_num]:
                            page_markdown = self._replace_image_placeholders_single_page(
                                page_markdown,
                                all_extracted_images[page_num],
                                page_num,
                                images_dir.name if images_dir else None
                            )

                        # Success - break retry loop
                        break

                    except Exception as e:
                        logger.error(f"Failed to process page {idx} (attempt {attempt}/{max_retries}): {e}")
                        if attempt < max_retries:
                            sleep_time = retry_delay * (2 ** (attempt - 1))  # exponential backoff
                            logger.info(f"Retrying in {sleep_time} seconds...")
                            time.sleep(sleep_time)
                        else:
                            logger.error(f"Page {idx} failed after {max_retries} attempts - skipping")
                            failed_pages.append({
                                'page_num': idx,
                                'image_path': image_path,
                                'error': str(e)
                            })
                            page_markdown = f"*[ERROR: Failed to process page {idx} after {max_retries} attempts]*\n\n"
                            page_markdown += f"*Error: {str(e)}*"

                # Append to file immediately (even if failed with error message)
                if output_path_obj and page_markdown:
                    self._append_markdown_page(output_path_obj, idx, page_markdown)

                logger.info(f"Progress: {idx}/{len(image_paths)} pages processed ({idx/len(image_paths)*100:.1f}%)")

            # Step 4: Finalize and save metadata
            if output_path_obj:
                logger.info(f"Completed Markdown conversion: {output_path}")

                # Report failed pages
                if failed_pages:
                    logger.warning(f"Failed to process {len(failed_pages)} page(s):")
                    for failed in failed_pages:
                        logger.warning(f"  - Page {failed['page_num']}: {failed['error']}")

                    # Save failed pages list to file
                    failed_pages_file = output_path_obj.parent / f"{output_path_obj.stem}_failed_pages.json"
                    with open(failed_pages_file, 'w', encoding='utf-8') as f:
                        json.dump(failed_pages, f, ensure_ascii=False, indent=2)
                    logger.warning(f"Failed pages list saved to: {failed_pages_file}")
                else:
                    logger.info("All pages processed successfully!")

                if all_extracted_images:
                    total_images = sum(len(imgs) for imgs in all_extracted_images.values())
                    logger.info(f"Total extracted images: {total_images}")

                    # Save JSON metadata if enabled
                    if Config.SAVE_IMAGE_METADATA_JSON:
                        self._save_image_metadata(
                            all_extracted_images,
                            output_path,
                            pdf_path_obj.stem
                        )

            success_rate = ((len(image_paths) - len(failed_pages)) / len(image_paths) * 100) if image_paths else 0
            return f"Conversion completed: {len(image_paths) - len(failed_pages)}/{len(image_paths)} pages successful ({success_rate:.1f}%)"

        finally:
            # Cleanup
            if image_extractor:
                image_extractor.close()
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")

    def _combine_markdown_pages(self, markdown_pages: list[str], document_name: str) -> str:
        """
        Combine individual page markdowns into a single document

        Args:
            markdown_pages: List of Markdown texts for each page
            document_name: Name of the source document

        Returns:
            Combined Markdown text
        """
        header = f"# {document_name}\n\n"
        header += f"*Converted from PDF using Zerox OCR approach with Amazon Bedrock Claude Haiku 4.5*\n\n"
        header += f"*Conversion date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        header += f"*Total pages: {len(markdown_pages)}*\n\n"
        header += "---\n\n"

        combined = header

        for idx, page_markdown in enumerate(markdown_pages, 1):
            combined += f"## Page {idx}\n\n"
            combined += page_markdown.strip()
            combined += "\n\n---\n\n"

        return combined

    def _replace_image_placeholders(
        self,
        markdown_pages: list[str],
        extracted_images: dict,
        page_start: int,
        images_dirname: Optional[str]
    ) -> list[str]:
        """
        Replace IMAGE_PLACEHOLDER with actual image paths and enhance metadata

        Args:
            markdown_pages: List of Markdown texts
            extracted_images: Dict of page_num -> list of image metadata
            page_start: Starting page number
            images_dirname: Name of images directory

        Returns:
            Updated list of Markdown texts
        """
        import re
        updated_pages = []

        for idx, markdown in enumerate(markdown_pages):
            page_num = page_start + idx

            # Check if this page has extracted images
            if page_num in extracted_images and images_dirname:
                images = extracted_images[page_num]

                # Replace each IMAGE_PLACEHOLDER with actual path and add metadata
                for img_idx, img_meta in enumerate(images):
                    if "IMAGE_PLACEHOLDER" in markdown:
                        # Use relative path for markdown
                        img_rel_path = f"{images_dirname}/{img_meta['filename']}"

                        # Build metadata comment
                        file_size_kb = img_meta.get('size', 0) / 1024 if 'size' in img_meta else 0
                        metadata_lines = [
                            f"File: {img_meta['filename']}",
                            f"Dimensions: {img_meta['width']}x{img_meta['height']}px",
                            f"Size: {file_size_kb:.1f}KB" if file_size_kb > 0 else "Size: N/A",
                            f"Format: {img_meta['format']}",
                            f"Page: {img_meta['page_num']}"
                        ]
                        metadata_text = " | ".join(metadata_lines)

                        # Find the placeholder and check if there's already a comment
                        # Pattern: ![title](IMAGE_PLACEHOLDER)\n<!-- ... -->
                        pattern = r'(!\[([^\]]*)\]\(IMAGE_PLACEHOLDER\))(\n<!--[^>]*-->)?'
                        match = re.search(pattern, markdown)

                        if match:
                            image_link = match.group(1)
                            existing_comment = match.group(3)

                            # Replace placeholder in image link
                            new_image_link = image_link.replace("IMAGE_PLACEHOLDER", img_rel_path)

                            if existing_comment:
                                # Claude generated a comment - enhance it with file metadata
                                enhanced_comment = existing_comment.rstrip('-->').rstrip()
                                enhanced_comment += f"\n{metadata_text} -->"
                                replacement = new_image_link + enhanced_comment
                            else:
                                # No comment - add basic metadata comment
                                replacement = new_image_link + f"\n<!-- {metadata_text} -->"

                            # Replace in markdown
                            markdown = markdown.replace(match.group(0), replacement, 1)
                            logger.info(f"Replaced placeholder with: {img_rel_path} (metadata added)")
                        else:
                            # Fallback: simple replacement if pattern doesn't match
                            markdown = markdown.replace("IMAGE_PLACEHOLDER", img_rel_path, 1)
                            logger.warning(f"Used fallback replacement for: {img_rel_path}")

            updated_pages.append(markdown)

        return updated_pages

    def _save_image_metadata(
        self,
        extracted_images: dict,
        output_path: str,
        document_name: str
    ):
        """
        Save image metadata as JSON file

        Args:
            extracted_images: Dict of page_num -> list of image metadata
            output_path: Path to the markdown output file
            document_name: Name of the document
        """
        if not extracted_images:
            return

        output_path_obj = Path(output_path)
        metadata_file = output_path_obj.parent / f"{output_path_obj.stem}_images_metadata.json"

        # Flatten images dict and add document context
        all_images = []
        for page_num, images in extracted_images.items():
            all_images.extend(images)

        metadata = {
            "document": document_name,
            "conversion_date": datetime.now().isoformat(),
            "total_pages": len(extracted_images),
            "total_images": len(all_images),
            "images": all_images
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved image metadata to: {metadata_file}")

    def _write_markdown_header(self, output_path: Path, document_name: str, total_pages: int):
        """
        Write Markdown header to file

        Args:
            output_path: Path to output file
            document_name: Name of the document
            total_pages: Total number of pages
        """
        header = f"# {document_name}\n\n"
        header += f"*Converted from PDF using Zerox OCR approach with Amazon Bedrock Claude Sonnet 4.5*\n\n"
        header += f"*Conversion date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        header += f"*Total pages: {total_pages}*\n\n"
        header += "---\n\n"

        output_path.write_text(header, encoding='utf-8')
        logger.info(f"Wrote header to: {output_path}")

    def _append_markdown_page(self, output_path: Path, page_num: int, page_markdown: str):
        """
        Append a page to the Markdown file

        Args:
            output_path: Path to output file
            page_num: Page number
            page_markdown: Markdown content for the page
        """
        page_content = f"## Page {page_num}\n\n"
        page_content += page_markdown.strip()
        page_content += "\n\n---\n\n"

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(page_content)

    def _replace_image_placeholders_single_page(
        self,
        page_markdown: str,
        extracted_images: list,
        page_num: int,
        images_dirname: Optional[str]
    ) -> str:
        """
        Replace IMAGE_PLACEHOLDER with actual image paths for a single page

        Args:
            page_markdown: Markdown text for single page
            extracted_images: List of image metadata for this page
            page_num: Page number
            images_dirname: Name of images directory

        Returns:
            Updated Markdown text
        """
        import re

        if not extracted_images or not images_dirname:
            return page_markdown

        # Pattern to match image markdown with optional HTML comment
        pattern = r'!\[([^\]]*)\]\(IMAGE_PLACEHOLDER\)(?:\s*<!--\s*(.*?)\s*-->)?'

        for img_meta in extracted_images:
            img_rel_path = f"{images_dirname}/{img_meta['filename']}"

            # Find next placeholder
            match = re.search(pattern, page_markdown)
            if match:
                alt_text = match.group(1)
                existing_comment = match.group(2)

                # Create metadata text
                metadata_text = f"File: {img_meta['filename']} | "
                metadata_text += f"Dimensions: {img_meta['width']}x{img_meta['height']}px | "
                metadata_text += f"Size: {img_meta['size']/1024:.1f}KB | "
                metadata_text += f"Format: {img_meta['format']} | "
                metadata_text += f"Page: {page_num}"

                # Create new image link
                new_image_link = f"![{alt_text}]({img_rel_path})"

                if existing_comment:
                    # Append metadata to existing comment
                    replacement = new_image_link + f"\n<!-- {existing_comment}\n{metadata_text} -->"
                else:
                    # Add basic metadata comment
                    replacement = new_image_link + f"\n<!-- {metadata_text} -->"

                # Replace in markdown
                page_markdown = page_markdown.replace(match.group(0), replacement, 1)
                logger.info(f"Replaced placeholder with: {img_rel_path}")
            else:
                # Fallback: simple replacement if pattern doesn't match
                page_markdown = page_markdown.replace("IMAGE_PLACEHOLDER", img_rel_path, 1)
                logger.warning(f"Used fallback replacement for: {img_rel_path}")

        return page_markdown


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown using AWS Bedrock Claude Haiku 4.5"
    )
    parser.add_argument(
        "pdf_path",
        help="Path to input PDF file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output Markdown file path (default: output/<pdf_name>.md)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=Config.PDF_DPI,
        help=f"DPI for PDF to image conversion (default: {Config.PDF_DPI})"
    )
    parser.add_argument(
        "--profile",
        default=Config.AWS_PROFILE,
        help=f"AWS profile name (default: {Config.AWS_PROFILE})"
    )
    parser.add_argument(
        "--region",
        default=Config.AWS_REGION,
        help=f"AWS region (default: {Config.AWS_REGION})"
    )
    parser.add_argument(
        "--first-page",
        type=int,
        help="First page to convert (1-indexed)"
    )
    parser.add_argument(
        "--last-page",
        type=int,
        help="Last page to convert (1-indexed)"
    )
    parser.add_argument(
        "--model",
        choices=["haiku", "sonnet"],
        default="sonnet",
        help="Claude model to use: haiku (faster, cheaper) or sonnet (more accurate)"
    )

    args = parser.parse_args()

    # Determine model ID based on selection
    if args.model == "haiku":
        model_id = Config.MODEL_ID_HAIKU
        logger.info(f"Using Claude Haiku 4.5 model: {model_id}")
    else:
        model_id = Config.MODEL_ID_SONNET
        logger.info(f"Using Claude Sonnet 4.5 model: {model_id}")

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        pdf_name = Path(args.pdf_path).stem
        page_suffix = ""
        if args.first_page:
            page_suffix = f"_p{args.first_page}"
            if args.last_page:
                page_suffix += f"-{args.last_page}"
        output_path = f"{Config.OUTPUT_DIR}/{pdf_name}{page_suffix}.md"

    # Initialize converter
    converter = PDFToMarkdownConverter(
        profile_name=args.profile,
        region_name=args.region,
        model_id=model_id
    )

    # Convert PDF
    try:
        markdown = converter.convert_pdf_to_markdown(
            args.pdf_path,
            output_path=output_path,
            dpi=args.dpi,
            first_page=args.first_page,
            last_page=args.last_page
        )
        logger.info("Conversion completed successfully!")
        logger.info(f"Output: {output_path}")
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise


if __name__ == "__main__":
    main()
