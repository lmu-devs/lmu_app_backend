import os
import zipfile
import tempfile
from datetime import datetime
from typing import List

from shared.core.logging import get_api_logger
from shared.core.exceptions import NotFoundError

logger = get_api_logger(__name__)

class LogService:
    def __init__(self):
        """Initialize the LogService."""
        self.log_directory = "logs"

    def get_log_files(self) -> List[str]:
        """Get all log files from the logs directory."""
        if not os.path.exists(self.log_directory):
            logger.error("Logs directory not found")
            raise NotFoundError(
                detail="Logs directory not found",
                extra={"directory": self.log_directory}
            )
        
        return [f for f in os.listdir(self.log_directory) if f.endswith('.log')]

    def create_log_archive(self) -> str:
        """Create a zip file containing all logs."""
        log_files = self.get_log_files()
        if not log_files:
            logger.error("No log files found")
            raise NotFoundError(
                detail="No log files found",
                extra={"directory": self.log_directory}
            )

        # Create a temporary zip file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f"logs_{timestamp}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for log_file in log_files:
                file_path = os.path.join(self.log_directory, log_file)
                zipf.write(file_path, log_file)
                logger.info(f"Added {log_file} to archive")

        return zip_path
