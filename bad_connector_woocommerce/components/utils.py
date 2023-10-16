import base64
import logging
import urllib.request

logger = logging.getLogger(__name__)


def fetch_image_data(image_url):
    """Fetch and encode an image from a URL as base64."""
    try:
        response = urllib.request.urlopen(image_url)
        if response.status == 200:
            binary_data = response.read()
            return base64.b64encode(binary_data).decode("utf-8")
        else:
            return None
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None
