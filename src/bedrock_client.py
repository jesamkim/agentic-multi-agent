"""
AWS Bedrock client for Claude Haiku 4.5 vision model integration
"""
import base64
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from PIL import Image

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BedrockClient:
    """Client for AWS Bedrock Claude Haiku 4.5 model"""

    def __init__(
        self,
        profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        model_id: Optional[str] = None
    ):
        """
        Initialize Bedrock client

        Args:
            profile_name: AWS profile name (defaults to Config.AWS_PROFILE)
            region_name: AWS region (defaults to Config.AWS_REGION)
            model_id: Bedrock model ID (defaults to Config.MODEL_ID)
        """
        self.profile_name = profile_name or Config.get_aws_profile()
        self.region_name = region_name or Config.get_aws_region()
        self.model_id = model_id or Config.get_model_id()

        # Initialize boto3 session with profile
        try:
            self.session = boto3.Session(
                profile_name=self.profile_name,
                region_name=self.region_name
            )
            self.bedrock_runtime = self.session.client('bedrock-runtime')
            logger.info(f"Initialized Bedrock client with profile: {self.profile_name}, region: {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise

    def encode_image_to_base64(self, image_path: str) -> tuple[str, str]:
        """
        Encode image to base64 string

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_string, media_type)
        """
        try:
            with Image.open(image_path) as img:
                # Determine media type
                format_lower = img.format.lower() if img.format else 'png'
                media_type = f"image/{format_lower}"

                # Read and encode
                with open(image_path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')

                return encoded, media_type
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise

    def image_to_markdown(
        self,
        image_path: str,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Convert image to Markdown using Claude Haiku 4.5

        Args:
            image_path: Path to image file
            system_prompt: System prompt (defaults to Config.SYSTEM_PROMPT)
            user_prompt: User prompt (defaults to Config.USER_PROMPT)
            max_tokens: Maximum tokens (defaults to Config.MAX_TOKENS)
            temperature: Temperature (defaults to Config.TEMPERATURE)

        Returns:
            Markdown text extracted from image
        """
        # Use defaults from config
        system_prompt = system_prompt or Config.SYSTEM_PROMPT
        user_prompt = user_prompt or Config.USER_PROMPT
        max_tokens = max_tokens or Config.MAX_TOKENS
        temperature = temperature or Config.TEMPERATURE

        # Encode image
        logger.info(f"Processing image: {image_path}")
        base64_image, media_type = self.encode_image_to_base64(image_path)

        # Prepare request body for Claude Messages API
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ]
        }

        try:
            # Invoke Bedrock model
            logger.info(f"Calling Bedrock model: {self.model_id}")
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            markdown_text = response_body['content'][0]['text']

            logger.info(f"Successfully processed image: {image_path}")
            return markdown_text

        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    def batch_images_to_markdown(
        self,
        image_paths: list[str],
        progress_callback: Optional[callable] = None
    ) -> list[str]:
        """
        Convert multiple images to Markdown

        Args:
            image_paths: List of image file paths
            progress_callback: Optional callback function(current, total)

        Returns:
            List of Markdown texts
        """
        markdown_results = []
        total = len(image_paths)

        for idx, image_path in enumerate(image_paths, 1):
            try:
                markdown = self.image_to_markdown(image_path)
                markdown_results.append(markdown)

                if progress_callback:
                    progress_callback(idx, total)
            except Exception as e:
                logger.error(f"Failed to process image {image_path}: {e}")
                markdown_results.append(f"[Error processing page {idx}: {str(e)}]")

        return markdown_results
