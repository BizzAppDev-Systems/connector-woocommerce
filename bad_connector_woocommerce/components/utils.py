import urllib.request
import base64


def fetch_image_data(image_url):
    try:
        response = urllib.request.urlopen(image_url)
        if response.status == 200:
            binary_data = response.read()
            return base64.b64encode(binary_data).decode('utf-8')
        else:
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None
