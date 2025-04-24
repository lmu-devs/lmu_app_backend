# publictransport/crawler/stop_crawler.py

import csv
import os
import re  # Needed for validator in model
from typing import List, Optional

# Adjust the import path based on your project structure
# Assuming models.py is in publictransport/models/
from publictransport.models.stop_models import MvvStop  # Import model and logger
from pydantic import ValidationError

# Default path for the input CSV. Configure as needed.
DEFAULT_MVV_STOP_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "MVV_HSTReport2412.csv"  # Point to the stop report
)


class MvvStopCrawler:
    """
    Reads MVV stop data from the HSTReport CSV file and returns
    structured stop data using the MvvStop Pydantic model.
    """

    def __init__(self, csv_filepath: str = DEFAULT_MVV_STOP_CSV_PATH):
        """
        Initializes the MvvStopCrawler.

        Args:
            csv_filepath (str): The path to the MVV stop report CSV file.
        """
        if not os.path.exists(csv_filepath):
            print(f"MVV Stop Report CSV file not found at: {csv_filepath}")
            raise FileNotFoundError(f"MVV Stop Report CSV file not found at: {csv_filepath}")
        self.csv_filepath = csv_filepath
        self.stops_raw_data = self._read_csv()

    def _read_csv(self) -> List[dict]:
        """Reads and parses the MVV stop report CSV file."""
        stops = []
        headers = []
        try:
            with open(self.csv_filepath, mode="r", encoding="utf-8") as infile:
                # Handle potential BOM
                first_char = infile.read(1)
                if first_char != "\ufeff":
                    infile.seek(0)

                reader = csv.reader(infile, delimiter=";", quotechar='"')
                raw_headers = next(reader)
                headers = [h.strip().strip('"') for h in raw_headers]
                print(f"CSV Headers found: {headers}")

                # Define expected headers based on the model aliases
                # Using aliases allows flexibility if CSV headers change slightly
                expected_headers = list(MvvStop.__fields__.keys())  # Get model field names
                aliases = {field.alias: name for name, field in MvvStop.__fields__.items()}

                # Check if required headers (aliases) are present
                missing_headers = [alias for alias in aliases if alias not in headers]
                if missing_headers:
                    raise ValueError(f"CSV file is missing required columns: {missing_headers}")

                header_map = {alias: headers.index(alias) for alias in aliases}

                for i, row in enumerate(reader):
                    if not row or len(row) < len(headers):  # Ensure row has enough columns
                        print(f"Skipping incomplete row {i+2}: {row}")
                        continue

                    # Create a dictionary using the original CSV headers as keys
                    raw_stop_data = {header: row[idx].strip() for header, idx in header_map.items()}

                    # Add any extra columns not defined in the Pydantic model explicitly
                    for idx, header in enumerate(headers):
                        if header not in raw_stop_data and len(row) > idx:
                            raw_stop_data[header] = row[idx].strip()  # Add extra data

                    stops.append(raw_stop_data)

            print(f"Successfully read {len(stops)} raw stop entries from {self.csv_filepath}")
            return stops

        except FileNotFoundError:
            print(f"Failed to find CSV file: {self.csv_filepath}")
            raise
        except ValueError as ve:  # Catch missing headers error
            print(f"Header validation failed for {self.csv_filepath}: {ve}")
            raise
        except Exception as e:
            print(f"Error reading or parsing CSV file {self.csv_filepath}: {e}")
            raise IOError(f"Error reading or parsing CSV file {self.csv_filepath}: {e}")

    def get_stops(self) -> List[MvvStop]:
        """
        Processes the raw CSV data and returns a list of MvvStop Pydantic models.

        Returns:
            List[MvvStop]: A list of processed MVV stop data.
        """
        processed_stops: List[MvvStop] = []
        validation_errors = 0
        for i, raw_stop in enumerate(self.stops_raw_data):
            try:
                # Pydantic will use the aliases defined in the model to map
                # the keys from raw_stop ('HstNummer', 'Name ohne Ort', etc.)
                # to the model fields (hst_nummer, name_ohne_ort, etc.)
                # It automatically handles type conversion (str -> int/float)
                stop_model = MvvStop(**raw_stop)
                processed_stops.append(stop_model)
            except ValidationError as e:
                validation_errors += 1
                print(f"Validation failed for stop data at original row {i+2}: {raw_stop}. Error: {e}")
            except Exception as e:  # Catch other unexpected errors during model creation
                validation_errors += 1
                print(f"Failed to create MvvStop model for raw data at row {i+2}: {raw_stop}. Error: {e}")

        if validation_errors > 0:
            print(f"Encountered {validation_errors} validation issues while processing stops.")
        print(f"Successfully processed {len(processed_stops)} MVV stop entries into models.")
        return processed_stops


# Example usage (can be removed or kept for testing)
if __name__ == "__main__":
    # Create a dummy CSV file for testing if the default one doesn't exist
    dummy_stop_filepath = DEFAULT_MVV_STOP_CSV_PATH
    if not os.path.exists(dummy_stop_filepath):
        os.makedirs(os.path.dirname(dummy_stop_filepath), exist_ok=True)
        dummy_stop_file_content = """"HstNummer";"Name ohne Ort";"Ort";"Globale ID";"WGS84 X";"WGS84 Y"
"1";"Karlsplatz (Stachus)";"München";"de:09162:1";"11.565396";"48.1393673"
"70";"Universität";"München";"de:09162:70";"11.580875";"48.150599"
"9999";"Invalid Coord Stop";"Testort";"de:99999:1";"200.0";"100.0"
"10000";"Missing Name";"";"de:10000:1";"11.5";"48.1"
"""  # Added invalid row for testing
        with open(dummy_stop_filepath, "w", encoding="utf-8") as f:
            f.write(dummy_stop_file_content)
        print(f"Created dummy stop file: {dummy_stop_filepath}")

    try:
        stop_crawler = MvvStopCrawler(csv_filepath=dummy_stop_filepath)
        stops = stop_crawler.get_stops()
        print(f"Successfully crawled {len(stops)} MVV stops.")
        for stop in stops[:5]:  # Print first 5 stops
            print(stop.model_dump_json(indent=2))

    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error during MVV stop crawl: {e}")

    # Optional: Clean up dummy file after testing
    # if os.path.exists(dummy_stop_filepath) and "dummy_stop_file_content" in locals():
    #     os.remove(dummy_stop_filepath)
    #     print(f"Removed dummy stop file: {dummy_stop_filepath}")
