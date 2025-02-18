import io
import os
from hashlib import md5
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image


class FaviconService:
    def __init__(self, save_directory="favicons"):
        """Initialize the FaviconService with a directory to save favicons."""
        self.save_directory = save_directory
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

    def save_favicon(self, url):
        """
        Save the favicon from a given URL as PNG.
        Returns the local path where the favicon was saved, or None if failed.
        """
        try:
            favicon_url = self.get_favicon_url(url)
            if not favicon_url:
                return None

            # Generate filename
            filename = md5(url.encode()).hexdigest() + '.png'
            local_path = os.path.join(self.save_directory, filename)

            # Download favicon
            response = requests.get(favicon_url, stream=True)
            response.raise_for_status()

            # Convert to PNG if necessary
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGBA if needed
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Save as PNG
            image.save(local_path, 'PNG')
            return local_path

        except Exception as e:
            print(f"Error saving favicon: {str(e)}")
            return None

    def get_favicon_url(self, url):
        """
        Get the favicon URL using faviconextractor.com with fallbacks.
        Returns the complete favicon URL or None if not found.
        """
        try:
            # Clean the URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            # Try faviconextractor.com first
            favicon_extractor_url = f"https://www.faviconextractor.com/api/favicon/{domain}?larger=true"
            response = requests.get(favicon_extractor_url)
            if response.status_code == 200:
                try:
                    # The API returns the actual favicon URL in the response
                    actual_favicon_url = response.json().get('favicon')
                    if actual_favicon_url:
                        return actual_favicon_url
                except:
                    pass  # If JSON parsing fails, move to fallback

            # First fallback: Google's favicon service
            google_favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
            response = requests.head(google_favicon_url)
            if response.status_code == 200:
                return google_favicon_url

            # Second fallback: Traditional method
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for favicon in HTML
            icon_links = soup.find_all('link', rel=lambda r: r and ('icon' in r.lower()))
            if icon_links:
                favicon_url = icon_links[0].get('href')
                if favicon_url and not favicon_url.startswith(('http://', 'https://')):
                    favicon_url = urljoin(url, favicon_url)
                return favicon_url

            # Last resort: Try default favicon.ico location
            return f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"

        except Exception as e:
            print(f"Error getting favicon URL: {str(e)}")
            return None


def main():
    # Test the FaviconService
    service = FaviconService()
    
    test_urls = [
        "lmu.de",
        "lmu-dev.org",
        "moodle.lmu.de",
        "lmu-app.lmu-dev.org",
    ]

    for url in test_urls:
        print(f"\nTesting URL: {url}")
        favicon_url = service.get_favicon_url(url)
        print(f"Favicon URL: {favicon_url}")
        saved_path = service.save_favicon(url)
        print(f"Saved favicon to: {saved_path}")


if __name__ == "__main__":
    main()
