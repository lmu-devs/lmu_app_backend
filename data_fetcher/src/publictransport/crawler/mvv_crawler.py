#!/usr/bin/env python3
import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MVVDepartureFetcher:
    BASE_URL = "https://www.mvv-muenchen.de/"
    DEPARTURES_ENDPOINT = "?eID=departuresFinder&action=get_departures"
    LINES_ENDPOINT = "?eID=departuresFinder&action=available_lines"
    SVG_BASE_URL = "https://www.mvv-muenchen.de/fileadmin/lines/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; MVVDepartureFetcher/1.0)",
                "Accept": "application/json",
            }
        )

    def add_svg_urls(self, data: dict) -> dict:
        """Add full SVG URLs to the response data for departures or lines."""
        if "departures" in data:
            for item in data["departures"]:
                if "line" in item and "symbol" in item["line"]:
                    symbol = item["line"]["symbol"]
                    item["line"]["symbol_url"] = f"{self.SVG_BASE_URL}{symbol}"
        elif "lines" in data:
            for item in data["lines"]:
                if "symbol" in item:
                    symbol = item["symbol"]
                    item["symbol_url"] = f"{self.SVG_BASE_URL}{symbol}"
        return data

    def get_departures(self, stop_id: str) -> dict:
        """
        Fetch departures for a given stop ID.

        Args:
            stop_id: The stop ID (e.g., 'de:09162:70') in the format 'de:xxxxx:yyyy'.

        Returns:
            dict: The JSON response from the API with added SVG URLs or an error dict.
        """
        original_input = stop_id

        if not self._validate_stop_id(stop_id):
            error_msg = f"Invalid stop_id format: '{stop_id}'. Expected format like 'de:xxxxx:yyyy'."
            logger.error(error_msg)
            return {"error": error_msg}

        # Always use current timestamp
        current_timestamp = int(time.time())

        params = {
            "stop_id": stop_id,
            "requested_timestamp": current_timestamp,
            "lines": "all",
        }

        try:
            response = self.session.get(f"{self.BASE_URL}{self.DEPARTURES_ENDPOINT}", params=params)
            response.raise_for_status()
            data = response.json()
            return self.add_svg_urls(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch departures: {e}", exc_info=True)
            return {"error": f"Failed to fetch departures: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse departures JSON response: {e}", exc_info=True)
            return {"error": f"Failed to parse departures response: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error fetching departures: {e}", exc_info=True)
            return {"error": f"Unexpected error fetching departures: {str(e)}"}

    def get_available_lines(self, stop_id: str) -> dict:
        """
        Fetch available lines for a given stop ID.

        Args:
            stop_id: The stop ID (e.g., 'de:09162:70') in the format 'de:xxxxx:yyyy'.

        Returns:
            dict: The JSON response from the API with added SVG URLs or an error dict.
        """
        original_input = stop_id

        if not self._validate_stop_id(stop_id):
            error_msg = f"Invalid stop_id format: '{stop_id}'. Expected format like 'de:xxxxx:yyyy'."
            logger.error(error_msg)
            return {"error": error_msg}

        params = {"stop_id": stop_id}

        try:
            response = self.session.get(f"{self.BASE_URL}{self.LINES_ENDPOINT}", params=params)
            response.raise_for_status()
            data = response.json()
            return self.add_svg_urls(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch available lines: {e}", exc_info=True)
            return {"error": f"Failed to fetch available lines: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse available lines JSON response: {e}", exc_info=True)
            return {"error": f"Failed to parse available lines response: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error fetching available lines: {e}", exc_info=True)
            return {"error": f"Unexpected error fetching available lines: {str(e)}"}

    def save_to_file(self, data: dict, filename: str):
        """Save the response data to a JSON file."""
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {str(e)}")

    def _validate_stop_id(self, stop_id: str) -> bool:
        """Check if the stop_id matches the expected format 'de:xxxx:yyyy'."""
        pattern = r"^de:\d+:[a-zA-Z0-9]+$"
        return bool(re.match(pattern, stop_id))


def parse_args():
    parser = argparse.ArgumentParser(description="MVV Departure and Line Information Fetcher")
    parser.add_argument(
        "action",
        choices=["departures", "lines"],
        help="Specify whether to fetch departures or available lines.",
    )
    parser.add_argument("stop_id", help="Stop ID (e.g., de:09162:70). Expected format 'de:xxxxx:yyyy'.")
    parser.add_argument("--save", help="Save the response to a JSON file", action="store_true")
    parser.add_argument(
        "--raw",
        help="Print raw JSON response instead of processed output",
        action="store_true",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    fetcher = MVVDepartureFetcher()

    response = None
    if args.action == "departures":
        logger.info(f"Fetching departures for stop ID: {args.stop_id}")
        response = fetcher.get_departures(args.stop_id)
    elif args.action == "lines":
        logger.info(f"Fetching available lines for stop ID: {args.stop_id}")
        response = fetcher.get_available_lines(args.stop_id)

    if not response or response.get("error"):
        logger.error(f"Error fetching data: {response.get('error', 'Unknown error')}")
        sys.exit(1)

    # Save response if requested
    if args.save:
        timestamp = int(time.time())
        stop_id_safe = args.stop_id.replace(":", "_")
        filename = f"{args.action}_{stop_id_safe}_{timestamp}.json"
        fetcher.save_to_file(response, filename)

    # Print JSON response if requested or not saved
    if args.raw or not args.save:
        print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
