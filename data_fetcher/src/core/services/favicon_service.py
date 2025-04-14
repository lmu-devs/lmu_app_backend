import os

import requests


class FaviconService:
    def __init__(self, save_directory="favicons"):
        """Initialize the FaviconService with a directory to save favicons."""
        self.save_directory = save_directory
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

    def get_favicon_url(self, url):
        """
        Get the favicon URL using allesedv.com with DuckDuckGo and Google as fallbacks.
        """
        try:
            # Clean the URL to get domain
            domain = url.split("/")[2] if "//" in url else url.split("/")[0]

            # Try icon.horse service first
            url = f"https://icon.horse/icon/{domain}"
            response = requests.head(url)
            if response.status_code == 200:
                return url

            # Try DuckDuckGo
            ddg_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
            response = requests.head(ddg_url)
            if response.status_code == 200:
                return ddg_url

            # Try allesedv.com
            allesedv_url = f"https://f3.allesedv.com/64/{domain}"
            response = requests.head(allesedv_url)
            if response.status_code == 200:
                return allesedv_url

            # Try Google's service first
            url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
            response = requests.head(url)
            if response.status_code == 200:
                return url

            return None

        except Exception as e:
            print(f"Error getting favicon URL: {str(e)}")
            return None


def main():
    # Test the FaviconService
    service = FaviconService()

    test_urls = [
        # "https://lmu.de",
        # "lmu-dev.org",
        # "https://moodle.lmu.de/my/",
        # "https://lmu-app.lmu-dev.org",
        "https://www.portal.uni-muenchen.de/benutzerkonto/#!/"
        # "https://mailbox.portal.uni-muenchen.de/webmail/webmail/ui/MainPage.html",
        # "https://auth.anny.eu/start-session?entityId=https://lmuidp.lrz.de/idp/shibboleth",
        # "https://lsf.verwaltung.uni-muenchen.de/qisserver/rds?state=user&type=0",
    ]

    for url in test_urls:
        print(f"\nTesting URL: {url}")
        favicon_url = service.get_favicon_url(url)
        print(f"Favicon URL: {favicon_url}")


if __name__ == "__main__":
    main()
