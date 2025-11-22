"""
PDF image extraction module using PyMuPDF
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional
import io

import fitz
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extract images from PDF documents"""

    def __init__(self, pdf_path: str):
        """
        Initialize image extractor

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        logger.info(f"Opened PDF: {pdf_path} ({self.doc.page_count} pages)")

    def extract_images_from_page(
        self,
        page_num: int,
        output_dir: str,
        min_width: int = 100,
        min_height: int = 100
    ) -> List[Dict[str, any]]:
        """
        Extract all images from a specific page

        Args:
            page_num: Page number (1-indexed)
            output_dir: Directory to save extracted images
            min_width: Minimum image width to extract
            min_height: Minimum image height to extract

        Returns:
            List of dictionaries containing image metadata
        """
        if page_num < 1 or page_num > self.doc.page_count:
            raise ValueError(f"Invalid page number: {page_num}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        page = self.doc[page_num - 1]  # Convert to 0-indexed
        image_list = page.get_images()

        extracted_images = []
        logger.info(f"Found {len(image_list)} images on page {page_num}")

        for img_index, img in enumerate(image_list, 1):
            try:
                xref = img[0]
                base_image = self.doc.extract_image(xref)

                if not base_image:
                    logger.warning(f"Could not extract image {img_index} from page {page_num}")
                    continue

                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                width = base_image["width"]
                height = base_image["height"]

                # Filter out small images (likely icons or decorations)
                if width < min_width or height < min_height:
                    logger.debug(f"Skipping small image: {width}x{height}")
                    continue

                # Save image
                image_filename = f"page_{page_num:03d}_img_{img_index:03d}.{image_ext}"
                image_path = output_path / image_filename

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                logger.info(f"Extracted image: {image_filename} ({width}x{height})")

                # Store metadata
                extracted_images.append({
                    "filename": image_filename,
                    "path": str(image_path),
                    "width": width,
                    "height": height,
                    "size": len(image_bytes),  # File size in bytes
                    "format": image_ext,
                    "page_num": page_num,
                    "index": img_index
                })

            except Exception as e:
                logger.error(f"Error extracting image {img_index} from page {page_num}: {e}")
                continue

        return extracted_images

    def save_page_as_image(
        self,
        page_num: int,
        output_path: str,
        dpi: int = 300,
        image_format: str = "PNG"
    ) -> str:
        """
        Save entire page as an image

        Args:
            page_num: Page number (1-indexed)
            output_path: Output file path
            dpi: Resolution
            image_format: Image format (PNG, JPEG, etc.)

        Returns:
            Path to saved image
        """
        if page_num < 1 or page_num > self.doc.page_count:
            raise ValueError(f"Invalid page number: {page_num}")

        page = self.doc[page_num - 1]

        # Create pixmap (image) from page
        zoom = dpi / 72  # PDF default is 72 DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Save image
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if image_format.upper() == "PNG":
            pix.save(output_path)
        else:
            # Convert to PIL Image for other formats
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(output_path, image_format)

        logger.info(f"Saved page {page_num} as {output_path}")
        return str(output_path)

    def get_page_info(self, page_num: int) -> Dict[str, any]:
        """
        Get information about a page

        Args:
            page_num: Page number (1-indexed)

        Returns:
            Dictionary with page information
        """
        if page_num < 1 or page_num > self.doc.page_count:
            raise ValueError(f"Invalid page number: {page_num}")

        page = self.doc[page_num - 1]
        rect = page.rect

        return {
            "page_num": page_num,
            "width": rect.width,
            "height": rect.height,
            "rotation": page.rotation,
            "image_count": len(page.get_images())
        }

    def close(self):
        """Close PDF document"""
        if self.doc:
            self.doc.close()
            logger.info(f"Closed PDF: {self.pdf_path}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
