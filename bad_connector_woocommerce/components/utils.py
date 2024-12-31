import base64
import logging

import requests

logger = logging.getLogger(__name__)


def fetch_image_data(image_url):
    """Fetch and encode an image from a URL as base64."""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            binary_data = response._content
            return base64.b64encode(binary_data).decode("utf-8")
        else:
            return None
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None


def chunks(items, length):
    """Splits a list into chunks of a specified length."""
    for index in range(0, len(items), length):
        yield items[index : index + length]
