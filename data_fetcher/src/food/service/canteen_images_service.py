import os
from typing import List, Tuple


class CanteenImageService:
    
    def generate_image_urls(directory_path: str, image_url_prefix: str) -> List[Tuple[str, str]]:
        files_with_urls = []
        
        # List all files in the directory
        files = os.listdir(directory_path)
        
        for file in files:
            # Extract the base name without the extension
            name = os.path.splitext(file)[0]
            
            # Format the location name
            # Remove the number suffix (_01, _02, etc.)
            base_name = name.rsplit('_', 1)[0]
            
            # Replace hyphens with spaces and capitalize words
            formatted_name = base_name.replace('-', ' ').title()
            
            # Create the full image URL
            full_image_url = f"{image_url_prefix}{file}"

            # Append a tuple with formatted location name and full URL
            files_with_urls.append((formatted_name, full_image_url))
        
        return files_with_urls