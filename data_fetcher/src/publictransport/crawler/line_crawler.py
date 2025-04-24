import csv
import math  # Needed for font size calculation
import os
import re
from typing import List, Optional

from publictransport.models.line_models import MvvLine

# Default path for the input CSV. Configure as needed.
DEFAULT_MVV_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "24-12-mvvlines_openData.csv")


class MvvCrawler:
    """
    Reads MVV line data from a specified CSV file, generates image URLs
    or fallback SVGs, and returns structured line data.
    """

    def __init__(self, csv_filepath: str = DEFAULT_MVV_CSV_PATH):
        """
        Initializes the MvvCrawler.

        Args:
            csv_filepath (str): The path to the MVV lines CSV file.
                                Expected columns: LINIENNR_EFA, VERKEHRSMITTEL, BRANCH_NR
                                Delimiter: ;
                                Quotes: "
        """
        if not os.path.exists(csv_filepath):
            print(f"MVV Lines CSV file not found at: {csv_filepath}")
            raise FileNotFoundError(f"MVV Lines CSV file not found at: {csv_filepath}")
        self.csv_filepath = csv_filepath
        self.lines_raw_data = self._read_csv()

    def _read_csv(self) -> List[dict]:
        """Reads and parses the MVV lines CSV file."""
        lines = []
        headers = []
        try:
            with open(self.csv_filepath, mode="r", encoding="utf-8") as infile:
                # Handle potential BOM (Byte Order Mark)
                first_char = infile.read(1)
                if first_char != "\ufeff":
                    infile.seek(0)  # Not a BOM, rewind

                reader = csv.reader(infile, delimiter=";", quotechar='"')
                raw_headers = next(reader)
                headers = [h.strip().strip('"') for h in raw_headers]  # Clean headers

                # Define expected headers
                expected_headers = ["LINIENNR_EFA", "VERKEHRSMITTEL", "BRANCH_NR"]

                # Verify headers or assume order
                if not all(h in headers for h in expected_headers):
                    print(f"CSV headers {headers} might not fully match expected {expected_headers}.")
                    if len(headers) < 3:
                        raise ValueError(
                            "CSV file must contain at least LINIENNR_EFA, VERKEHRSMITTEL, BRANCH_NR columns"
                        )
                    # Assume standard order if headers are different but minimum present
                    header_map = {
                        expected_headers[0]: headers[0],
                        expected_headers[1]: headers[1],
                        expected_headers[2]: headers[2],
                    }
                else:
                    header_map = {h: h for h in expected_headers}

                for i, row in enumerate(reader):
                    if not row or len(row) < len(header_map):  # Check against mapped headers
                        print(f"Skipping incomplete row {i+2}: {row}")
                        continue

                    line_data = {}
                    try:
                        # Map expected headers to their values in the row
                        for expected_h, actual_h in header_map.items():
                            line_data[expected_h] = row[headers.index(actual_h)].strip()

                        # Add any extra columns found
                        for idx, extra_header in enumerate(headers[len(header_map) :]):
                            if len(row) > len(header_map) + idx:
                                line_data[extra_header] = row[len(header_map) + idx].strip()

                        lines.append(line_data)

                    except IndexError:
                        print(f"Skipping row {i+2} due to insufficient columns: {row}")
                        continue

            print(f"Successfully read {len(lines)} lines from {self.csv_filepath}")
            return lines

        except FileNotFoundError:
            print(f"Failed to find CSV file: {self.csv_filepath}")
            raise
        except Exception as e:
            print(f"Error reading or parsing CSV file {self.csv_filepath}: {e}")
            raise IOError(f"Error reading or parsing CSV file {self.csv_filepath}: {e}")

    def _clean_liniennr(self, liniennr_efa: str) -> str:
        """Removes common suffixes like V or W."""
        return re.sub(r"[VW]$", "", liniennr_efa)

    def _get_numeric_part(self, liniennr_efa: str) -> str:
        """Extracts the numeric part of a line number string."""
        match = re.search(r"\d+$", liniennr_efa)  # Match digits at the end
        return match.group(0) if match else liniennr_efa

    def _generate_image_url(self, line_data: dict) -> Optional[str]:
        """
        Generates the expected image URL for a given line data dictionary.

        Args:
            line_data (dict): A dictionary representing a single line from the CSV.

        Returns:
            str or None: The generated URL string, or None.
        """
        efa = line_data.get("LINIENNR_EFA")
        mittel = line_data.get("VERKEHRSMITTEL")
        branch = line_data.get("BRANCH_NR")
        base_url = "https://www.mvv-muenchen.de/fileadmin/lines/"

        if not efa or not mittel or not branch:
            print(f"Missing required data to generate URL for: {line_data}")
            return None

        cleaned_efa = self._clean_liniennr(efa)
        numeric_part_efa = self._get_numeric_part(efa)

        try:
            if mittel == "ExpressBus":
                if efa == "HEX":
                    return f"{base_url}15HEX.svg"
                if efa == "Lufthansa Express Bus":
                    return f"{base_url}15.svg"  # Special case
                if efa.startswith("X"):
                    effective_branch = "15" if efa == "X400" else branch
                    numeric_part_for_x = re.search(r"\d+", efa)
                    if numeric_part_for_x:
                        return f"{base_url}{effective_branch}{numeric_part_for_x.group(0)}.svg"
                    else:
                        print(f"Could not extract numeric part for ExpressBus: {efa}")
                        return None
                else:
                    print(f"Unhandled ExpressBus type for URL generation: {efa}")
                    return None
            elif mittel == "FLEXlinie":
                return f"{base_url}{branch}{efa}.svg"
            elif mittel == "MetroBus":
                padded_efa = numeric_part_efa.zfill(3)
                return f"{base_url}{branch}{padded_efa}.svg"
            elif mittel == "NachtBus":
                return f"{base_url}33{efa}.svg"
            elif mittel == "NachtTram":
                return f"{base_url}32{efa}.svg"
            elif mittel == "RegionalBus":
                return f"{base_url}{branch}{cleaned_efa}.svg"
            elif mittel == "S-Bahn":
                s_num = efa.replace("S", "")
                if efa == "S1":
                    return f"{base_url}92MD1.svg"
                else:
                    padded_s_num = s_num.zfill(2) if len(s_num) == 1 else s_num
                    return f"{base_url}92M{padded_s_num}.svg"
            elif mittel == "StadtBus":
                if re.match(r"^1\d{2}$", cleaned_efa):
                    return f"{base_url}03{cleaned_efa}.svg"
                else:
                    return f"{base_url}{branch}{cleaned_efa}.svg"
            elif mittel == "Tram":
                return f"{base_url}020{numeric_part_efa}.svg"
            elif mittel == "U-Bahn":
                # Ensure 'U' is removed before padding if needed, though U-Bahn numbers are single usually
                u_num_part = efa.replace("U", "")
                return f"{base_url}010{u_num_part}.svg"  # e.g., 0101, 0106
            elif mittel in ["Regionalzug", "RufTaxi"]:
                return None  # No URL pattern known
            else:
                print(f"Unknown URL pattern for VERKEHRSMITTEL '{mittel}'.")
                return None
        except Exception as url_error:
            print(f"Error generating URL for {line_data}: {url_error}")
            return None

    def _generate_fallback_svg(self, line_data: dict) -> Optional[str]:
        """
        Generates a fallback SVG string with the LINIENNR_EFA centered.

        Args:
            line_data (dict): A dictionary representing a single line.

        Returns:
            str or None: The generated SVG string, or None if LINIENNR_EFA is missing.
        """
        text_content = line_data.get("LINIENNR_EFA")
        if not text_content:
            print(f"Missing LINIENNR_EFA for fallback SVG generation in: {line_data}")
            return None

        viewbox_width = 1000
        viewbox_height = 500
        max_font_size = viewbox_height * 0.85
        avg_char_width_ratio = 0.6
        max_text_width = viewbox_width * 0.95
        font_size_width = max_text_width / (max(1, len(text_content)) * avg_char_width_ratio)
        font_size = int(min(max_font_size, font_size_width))

        # Basic escaping for XML safety
        safe_text = text_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        svg_template = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" id="Ebene_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox='0 0 {viewbox_width} {viewbox_height}' xml:space="preserve">
<rect fill="transparent" width="{viewbox_width}" height="{viewbox_height}"/>
<text text-anchor="middle" x="50%" y="50%" dy=".35em" font-family="Arial, sans-serif" font-weight="bold" font-size="{font_size}px" fill="#808080">{safe_text}</text>
</svg>"""
        return svg_template.strip()

    def get_lines(self) -> List[MvvLine]:
        """
        Processes the raw CSV data to generate image URLs or fallback SVGs
        and returns a list of MvvLine Pydantic models.

        Returns:
            List[MvvLine]: A list of processed MVV line data.
        """
        processed_lines: List[MvvLine] = []
        for raw_line in self.lines_raw_data:
            liniennr_efa = raw_line.get("LINIENNR_EFA")
            verkehrsmittel = raw_line.get("VERKEHRSMITTEL")
            branch_nr = raw_line.get("BRANCH_NR")

            if not liniennr_efa or not verkehrsmittel or not branch_nr:
                continue

            image_url = self._generate_image_url(raw_line)
            fallback_svg = None
            if not image_url and verkehrsmittel not in ["Regionalzug", "RufTaxi"]:
                # Generate fallback only if URL generation failed and it's not an explicitly skipped type
                fallback_svg = self._generate_fallback_svg(raw_line)

            try:
                mvv_line = MvvLine(
                    liniennr_efa=liniennr_efa,
                    verkehrsmittel=verkehrsmittel,
                    branch_nr=branch_nr,
                    image_url=image_url,
                    fallback_svg=fallback_svg,
                    # Map any extra fields if needed and defined in MvvLine model
                )
                processed_lines.append(mvv_line)
            except Exception as e:  # Catch potential Pydantic validation errors etc.
                print(f"Error creating MvvLine model for {raw_line}: {e}")
        return processed_lines


# Example usage (can be removed or kept for testing)
if __name__ == "__main__":
    # Create a dummy CSV file for testing if it doesn't exist
    dummy_filepath = DEFAULT_MVV_CSV_PATH
    if not os.path.exists(dummy_filepath):
        os.makedirs(os.path.dirname(dummy_filepath), exist_ok=True)
        dummy_file_content = """"LINIENNR_EFA";"VERKEHRSMITTEL";"BRANCH_NR"
"U1";"U-Bahn";"21"
"S1";"S-Bahn";"1"
"S2";"S-Bahn";"1"
"S20";"S-Bahn";"1"
"50";"MetroBus";"24"
"211V";"RegionalBus";"19"
"211";"RegionalBus";"19"
"716";"RegionalBus";"65"
"HEX";"ExpressBus";"15"
"X200";"ExpressBus";"20"
"X400";"ExpressBus";"15"
"100";"StadtBus";"23"
"290";"StadtBus";"19"
"12";"Tram";"22"
"999";"UnknownType";"99"
"RB 16";"Regionalzug";"8"
"""
        with open(dummy_filepath, "w", encoding="utf-8") as f:
            f.write(dummy_file_content)
        print(f"Created dummy file: {dummy_filepath}")

    try:
        crawler = MvvCrawler(csv_filepath=dummy_filepath)
        lines = crawler.get_lines()
        print(f"Successfully crawled {len(lines)} MVV lines.")
        for line in lines[:5]:  # Print first 5 lines
            print(line.model_dump_json(indent=2))

    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error during MVV crawl: {e}")

    # Optional: Clean up dummy file after testing
    # if os.path.exists(dummy_filepath) and "dummy_file_content" in locals():
    #     os.remove(dummy_filepath)
    #     print(f"Removed dummy file: {dummy_filepath}")
