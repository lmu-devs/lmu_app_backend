import os

from typing import List, Tuple

class ImageService:
    
    def generate_image_urls(directory_path: str, image_url_prefix: str) -> List[Tuple[str, str]]:
        files_with_urls = []
        
        # List all files in the directory
        files = os.listdir(directory_path)
        
        for file in files:
            # Extract the base name without the extension
            base_name = os.path.splitext(file)[0]
            
            # Split the base name at '+' and take the first part
            location_name = base_name.split('+')[0]
            
            # Create the full image URL
            full_image_url = f"{image_url_prefix}{file}"

            # Append a tuple with location name and full URL
            files_with_urls.append((location_name, full_image_url))
        
        return files_with_urls