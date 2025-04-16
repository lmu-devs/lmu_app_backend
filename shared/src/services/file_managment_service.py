import os
import urllib.request
from pathlib import Path


class FileManagementService:
    def __init__(self, base_path: str = "shared/src/assets"):
        self.base_path = base_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Ensures the base directory exists, creates it if it doesn't"""
        Path(self.base_path).mkdir(parents=True, exist_ok=True)

    async def save_file_from_url(self, url: str, filename: str | None) -> str:
        """
        Downloads and saves a file from a URL to the base path
        Returns the full path to the saved file
        """
        if filename is None:
            # Extract filename from URL or generate a unique name
            filename = os.path.basename(url) or f"file_{hash(url)}"

        full_path = os.path.join(self.base_path, filename)

        # Download and save the file
        urllib.request.urlretrieve(url, full_path)

        return full_path

    def save_file_from_path(self, source_path: str, filename: str | None) -> str:
        """
        Copies a file from a source path to the base path
        Returns the full path to the saved file
        """
        if filename is None:
            filename = os.path.basename(source_path)

        full_path = os.path.join(self.base_path, filename)

        # Copy the file
        os.replace(source_path, full_path)

        return full_path

    def generate_save_file_name(filename: str) -> str:
        # Replace spaces with underscores and remove special characters
        safe_filename = "".join(
            ("_" if char.isspace() else char if char.isalnum() or char == "_" or char == "." else "")
            for char in filename
        )
        return safe_filename

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Safely delete a file

        Args:
            file_path: Path to the file to delete

        Returns:
            bool: True if file was deleted successfully, False if file doesn't exist

        Raises:
            Exception: If deletion fails for any other reason
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            raise Exception(f"Failed to delete file {file_path}: {str(e)}")


if __name__ == "__main__":
    service = FileManagementService("shared/assets/dishes")
    # Example usage
    # saved_path = service.save_file_from_path("/private/var/folders/wl/9gn5jspx0gz7w70qz0rnqxn00000gn/T/gradio/0954d4102a032625bfa1d14684277238be34ccfb1821105a0735a879f225b979/output.png", "test_image.jpg")
    print(service.generate_save_file_name("test_image0Äsld JJsl Lol!!***§.jpg"))
    # print(f"File saved to: {saved_path}")
