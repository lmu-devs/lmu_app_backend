import json
import os
from typing import Optional

from ..models.library_model import Libraries


class LibraryService:
    def __init__(self):
        self._data: Optional[Libraries] = None

    def _load_data(self) -> Libraries:
        if self._data is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(current_dir, "libraries.json")
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._data = Libraries(**data)
        return self._data

    def get_libraries(self, library_id: Optional[str] = None) -> Libraries:
        data = self._load_data()
        if library_id:
            filtered_libraries = [lib for lib in data.libraries if lib.id == library_id]
            return Libraries(libraries=filtered_libraries)
        return data
