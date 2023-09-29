import urllib.request


def fetch_image_data(image_url):
    try:
        response = urllib.request.urlopen(image_url)
        if response.status == 200:
            return response.read()
        else:
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None
