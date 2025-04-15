"""
LMU Main News Crawler

This module provides functionality to crawl and extract news articles from the LMU website.
It handles fetching both article content and associated images.
"""

import json
import logging
import os
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Represents a news article from LMU."""

    title: str
    date: datetime
    link: str
    description: str
    image_url: Optional[str] = None


class LMUMainNewsCrawler:
    """Crawler for fetching news articles from the LMU website."""

    def __init__(self):
        """Initialize the crawler with base URLs and configuration."""
        self.base_url = "https://www.lmu.de"
        self.news_api_url = "https://www.lmu.de/api/caas/30lmu.release.content/"
        self.image_api_url = "https://www.lmu.de/api/caas/00mm.release.content/"
        self.data_dir = Path("data_samples")
        self.data_dir.mkdir(exist_ok=True)

    def _save_debug_data(self, data: dict, prefix: str) -> None:
        """
        Save API response data for debugging purposes.

        Args:
            data: The data to save
            prefix: Prefix for the filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f"{prefix}_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Debug data saved to: {output_file}")

    def _make_api_request(self, url: str, params: dict) -> dict:
        """
        Make an API request with error handling.

        Args:
            url: The API endpoint URL
            params: Query parameters for the request

        Returns:
            The JSON response data

        Raises:
            requests.RequestException: If the API request fails
        """
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def extract_image_urls(self, response_data: dict) -> Dict[str, str]:
        """
        Extract medium-sized image URLs from API response.

        Args:
            response_data: The API response containing image data

        Returns:
            Dictionary mapping image IDs to their URLs
        """
        image_urls = {}

        if "_embedded" in response_data and "rh:doc" in response_data["_embedded"]:
            for doc in response_data["_embedded"]["rh:doc"]:
                if (
                    doc.get("fsType") == "Media"
                    and "resolutionsMetaData" in doc
                    and "1_1_format_m" in doc["resolutionsMetaData"]
                ):

                    image_id = doc["identifier"]
                    image_urls[image_id] = doc["resolutionsMetaData"]["1_1_format_m"]["url"]

        logger.info(f"Found {len(image_urls)} image URLs")
        return image_urls

    def fetch_images(self, image_ids: List[str]) -> Dict[str, str]:
        """
        Fetch image URLs for given image IDs.

        Args:
            image_ids: List of image IDs to fetch

        Returns:
            Dictionary mapping image IDs to their URLs
        """
        if not image_ids:
            return {}

        params = {
            "pagesize": "50",
            "page": "1",
            "filter": json.dumps({"$or": [{"_id": image_id} for image_id in image_ids]}),
        }

        try:
            response_data = self._make_api_request(self.image_api_url, params)
            return self.extract_image_urls(response_data)
        except requests.RequestException:
            return {}

    def _parse_article(self, item: dict) -> Optional[tuple[Article, Optional[str]]]:
        """
        Parse a single article item from the API response.

        Args:
            item: Article data from API

        Returns:
            Tuple of (Article object, image_id) if valid, None otherwise
        """
        if item.get("fsType") != "Dataset" or item.get("schema") != "Newsroom":
            return None

        form_data = item.get("formData", {})

        title = form_data.get("tt_title", {}).get("value")
        date_str = form_data.get("tt_date", {}).get("value")
        description = form_data.get("tt_teaser_text", {}).get("value")
        link = f"{self.base_url}{item.get('route', '')}" if item.get("route") else None

        image_id = None
        if tt_teaser_image := form_data.get("tt_teaser_image", {}).get("value"):
            image_id = tt_teaser_image.get("identifier")
            if image_id:
                image_id = f"{image_id}.de_DE"

        if all([title, date_str, link]):
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            article = Article(
                title=title,
                date=date,
                link=link,
                description=description or "",
                image_url=None,
            )
            return article, image_id

        return None

    def fetch_news(self) -> List[Article]:
        """
        Fetch news articles from LMU website.

        Returns:
            List of Article objects
        """
        params = {
            "rep": "hal",
            "count": "true",
            "hal": "f",
            "page": "1",
            "pagesize": "50",
            "sort": json.dumps({"formData.tt_date": -1}),
            "filter": [
                json.dumps({"schema": "Newsroom"}),
                json.dumps(
                    {
                        "$or": [
                            {
                                "entityType": "news",
                                "locale.identifier": "DE",
                                "formData.tt_formats.value": {"$elemMatch": {"identifier": "nr"}},
                                "formData.tt_lang_translated.value": {"$elemMatch": {"identifier": "DE"}},
                            },
                            {
                                "entityType": "videos",
                                "locale.identifier": "DE",
                                "formData.tt_lang_translated.value": {"$elemMatch": {"identifier": "DE"}},
                            },
                            {
                                "entityType": "social_medias",
                                "locale.identifier": "DE",
                                "formData.tt_lang_translated.value": {"$elemMatch": {"identifier": "DE"}},
                            },
                            {
                                "entityType": "gallery",
                                "locale.identifier": "DE",
                                "formData.tt_lang_translated.value": {"$elemMatch": {"identifier": "DE"}},
                            },
                        ]
                    }
                ),
            ],
        }

        try:
            # Fetch and parse news data
            response_data = self._make_api_request(self.news_api_url, params)
            self._save_debug_data(response_data, "lmu_news_response")

            articles = []
            image_ids = []
            articles_by_image = {}

            # Parse articles and collect image IDs
            for item in response_data.get("_embedded", {}).get("rh:doc", []):
                result = self._parse_article(item)
                if result:
                    article, image_id = result
                    articles.append(article)
                    if image_id:
                        image_ids.append(image_id)
                        articles_by_image[image_id.replace(".de_DE", "")] = article

            # Fetch and associate images
            image_urls = self.fetch_images(image_ids)
            for image_id, url in image_urls.items():
                base_image_id = image_id.replace(".de_DE", "")
                if article := articles_by_image.get(base_image_id):
                    article.image_url = url

            logger.info(f"Successfully fetched {len(articles)} articles")
            return articles

        except requests.RequestException as e:
            logger.error(f"Failed to fetch news: {e}")
            return []


def main():
    """Main entry point for the crawler."""
    crawler = LMUMainNewsCrawler()
    articles = crawler.fetch_news()

    print(f"\nFound {len(articles)} articles:")
    for article in articles:
        print(f"\nDate: {article.date}")
        print(f"Title: {article.title}")
        print(f"Link: {article.link}")
        print(f"Image: {article.image_url}")
        print(f"Description: {article.description}")
        print("-" * 50)


if __name__ == "__main__":
    main()
