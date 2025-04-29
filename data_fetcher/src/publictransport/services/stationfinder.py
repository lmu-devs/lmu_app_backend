import csv
import json  # Keep for printing structured data if needed, though not saving
import math
import time  # Added for departure time formatting
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from publictransport.crawler.mvv_crawler import MVVDepartureFetcher


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points
    on the earth (specified in decimal degrees) using the Haversine formula.
    Returns the distance in kilometers.
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers. Use 6371 for kilometers
    r = 6371
    return c * r


def find_stations_within_radius(
    latitude: float,
    longitude: float,
    radius_km: float,
    csv_filepath: str = "MVV_HSTReport2412.csv",
) -> List[Dict]:
    """
    Finds all stations from the MVV CSV file within a specified radius
    from the given latitude and longitude.

    Args:
        latitude: The latitude of the center point.
        longitude: The longitude of the center point.
        radius_km: The radius in kilometers.
        csv_filepath: The path to the MVV station CSV file.

    Returns:
        A list of dictionaries, where each dictionary represents a station
        within the radius and contains 'name', 'latitude', 'longitude',
        'stop_id', and 'distance_km'. Returns an empty list if the file is not found
        or no stations are within the radius.
    """
    stations_within_radius = []
    csv_file = Path(csv_filepath)
    if not csv_file.is_file():
        print(f"Error: CSV file not found at {csv_filepath}")
        # Try looking in the 'publictransport' directory as a fallback
        csv_file = Path("publictransport") / csv_filepath
        if not csv_file.is_file():
            print(f"Error: Also not found at {csv_file}")
            return []
        else:
            print(f"Using CSV file found at: {csv_file}")
            csv_filepath = str(csv_file)

    try:
        with open(csv_filepath, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter=";")
            try:
                header = next(reader)  # Skip the header row
            except StopIteration:
                print("Error: CSV file is empty.")
                return []

            # Get indices based on header names
            try:
                name_idx = header.index("Name ohne Ort")
                ort_idx = header.index("Ort")
                lat_idx = header.index("WGS84 X")
                lon_idx = header.index("WGS84 Y")
                stop_id_idx = header.index("Globale ID")  # Added stop_id index
            except ValueError as e:
                print(f"Error: Required column not found in CSV header - {e}")
                return []

            for row in reader:
                # Check if row has enough columns before accessing indices
                if len(row) <= max(name_idx, ort_idx, lat_idx, lon_idx, stop_id_idx):
                    # print(f"Skipping row due to insufficient columns: {row}")
                    continue

                try:
                    station_name = row[name_idx].strip()
                    station_ort = row[ort_idx].strip()
                    full_name = f"{station_name} ({station_ort})" if station_ort else station_name
                    stop_id = row[stop_id_idx].strip()  # Get the stop ID

                    # Skip rows with empty coordinates or stop_id
                    if not row[lat_idx] or not row[lon_idx] or not stop_id:
                        # print(f"Skipping row with missing data: {row}")
                        continue

                    # Replace comma with period for decimal conversion
                    station_lat_str = row[lat_idx].replace(",", ".")
                    station_lon_str = row[lon_idx].replace(",", ".")

                    station_lat = float(station_lat_str)
                    station_lon = float(station_lon_str)

                    # Calculate distance
                    distance = haversine(latitude, longitude, station_lat, station_lon)

                    if distance <= radius_km:
                        stations_within_radius.append(
                            {
                                "name": full_name,
                                "latitude": station_lat,
                                "longitude": station_lon,
                                "stop_id": stop_id,  # Included stop_id
                                "distance_km": round(distance, 3),  # Round distance for readability
                            }
                        )

                except (ValueError, IndexError) as e:
                    # Log less critical errors, like parsing floats
                    # print(f"Skipping row due to parsing error: {row} - {e}")
                    continue  # Skip rows with invalid data

    except FileNotFoundError:
        # This case is handled by the Path check at the beginning
        pass
    except Exception as e:
        print(f"An unexpected error occurred reading CSV: {e}")
        return []

    # Sort stations by distance
    stations_within_radius.sort(key=lambda x: x["distance_km"])

    return stations_within_radius


# --- Main execution block ---
if __name__ == "__main__":
    # Example coordinates (e.g., near Universität, Munich)
    center_lat = 48.149012  # Example: Universität lat
    center_lon = 11.580515  # Example: Universität lon
    search_radius = 0.35  # kilometers - Adjust as needed

    print(f"Finding stations within {search_radius} km of ({center_lat}, {center_lon})...")

    # Use the absolute path or adjust relative path as needed for the CSV
    script_dir = Path(__file__).parent
    # Try finding the CSV relative to the script first, then in parent, then grandparent
    csv_paths_to_try = [
        script_dir / "MVV_HSTReport2412.csv",
        script_dir.parent / "MVV_HSTReport2412.csv",
        script_dir.parent.parent / "MVV_HSTReport2412.csv",
        Path("MVV_HSTReport2412.csv"),  # Current dir as last resort
    ]
    found_csv_path = None
    for path_attempt in csv_paths_to_try:
        if path_attempt.is_file():
            found_csv_path = str(path_attempt)
            print(f"Using CSV file: {found_csv_path}")
            break

    if not found_csv_path:
        print("Error: MVV_HSTReport2412.csv not found in script directory or parent directories.")
        exit()

    nearby_stations = find_stations_within_radius(center_lat, center_lon, search_radius, csv_filepath=found_csv_path)

    unique_lines_info = set()  # Store tuples of (number, name)
    departures_by_station = {}  # Store departures for each station

    if nearby_stations:
        print(f"\nFound {len(nearby_stations)} stations:")
        for station in nearby_stations:
            print(f"  - {station['name']} (ID: {station['stop_id']}) - {station['distance_km']} km")

        # Check if MVVDepartureFetcher was imported successfully
        if MVVDepartureFetcher:
            print("\nFetching available lines and upcoming departures for found stations...")
            current_fetch_time = int(time.time())
            print(f"Current timestamp for departure requests: {current_fetch_time} (Epoch)")
            mvv_fetcher = MVVDepartureFetcher()
            processed_stop_ids = set()  # To avoid fetching the same stop_id multiple times

            for station in nearby_stations:
                stop_id = station.get("stop_id")
                station_name = station.get("name")
                if not stop_id or stop_id in processed_stop_ids:
                    continue  # Skip if no stop_id or already processed

                print(f"\n--- Processing Station: {station_name} (ID: {stop_id}) ---")
                processed_stop_ids.add(stop_id)

                # --- Fetch Available Lines ---
                lines_data = mvv_fetcher.get_available_lines(stop_id)
                if not lines_data.get("error"):
                    if "lines" in lines_data:
                        for line in lines_data["lines"]:
                            line_number = line.get("number")
                            line_name = line.get("name")
                            if line_number and line_name:
                                unique_lines_info.add((line_number, line_name))
                    else:
                        print(f"  No 'lines' data found for {station_name}")
                else:
                    print(f"  Error fetching lines for {station_name}: {lines_data['error']}")

                # --- Fetch Departures ---
                # departures_data = mvv_fetcher.get_departures(stop_id)
                # if not departures_data.get("error"):
                #     departures_by_station[station_name] = departures_data.get("departures", [])
                # else:
                #      print(f"  Error fetching departures for {station_name}: {departures_data['error']}")
                #      departures_by_station[station_name] = []

            # --- Print Unique Lines Found ---
            if unique_lines_info:
                print("\n--- Unique Lines Serving Nearby Stations ---")

                # Sort lines by number, handling potential non-numeric lines
                def sort_key(line_info):
                    try:
                        return (
                            0,
                            int(line_info[0]),
                            line_info[1],
                        )  # Sort numbers first
                    except ValueError:
                        return (1, line_info[0], line_info[1])  # Sort non-numbers after

                sorted_lines = sorted(list(unique_lines_info), key=sort_key)
                for number, name in sorted_lines:
                    print(f"  - Line {number} ({name})")
            else:
                print("\nNo line information collected.")

            # --- Print Next 5 Departures (Full JSON) ---
            print("\n--- Next 5 Departures per Station (Full JSON) ---")
            if departures_by_station:
                for station_name, departures in departures_by_station.items():
                    print(f"\n  Station: {station_name}")
                    if departures:
                        departures.sort(
                            key=lambda d: (
                                d.get("departureTime") if d.get("departureTime") is not None else float("inf")
                            )
                        )
                        count = 0
                        for dep in departures:
                            if count >= 5:
                                break
                            print(f"    Departure {count + 1}:")
                            print(f"{json.dumps(dep, indent=6, ensure_ascii=False)}")
                            count += 1
                    else:
                        print("    No departure information found.")
            else:
                print("  No departure data collected.")

        else:
            print("\nSkipping line and departure fetching because MVVDepartureFetcher could not be imported.")

    else:
        print("\nNo stations found within the specified radius.")
