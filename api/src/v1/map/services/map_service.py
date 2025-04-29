import json
import os

from api.src.v1.map.models.map_model import ThemeEnum


class MapService:
    def __init__(self):
        self._data: dict = None

    async def get_map_style(self, theme: ThemeEnum):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if theme == ThemeEnum.LIGHT:
            json_path = os.path.join(current_dir, "constants/lmu_students_base_map_light.json")
        else:
            json_path = os.path.join(current_dir, "constants/lmu_students_base_map_dark.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
