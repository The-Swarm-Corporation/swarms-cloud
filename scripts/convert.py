import base64
import requests


def download_and_encode_image(image_url):
    """
    Downloads an image from a URL and encodes it into a base64 string.
    Args:
        image_url (str): The URL to the image file.

    This function fetches the specified image from the URL, reads its content, and encodes it into a base64 string.
    The base64 encoding is used to send images over HTTP as text.
    """

    # Download the image
    response = requests.get(image_url)
    # Ensure the request was successful
    if response.status_code == 200:
        # Encode the image content to base64
        return base64.b64encode(response.content).decode("utf-8")
    else:
        print("Failed to download the image.")
        return None


image_path = "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg"
encoded_image = download_and_encode_image(image_path)
print(encoded_image)
