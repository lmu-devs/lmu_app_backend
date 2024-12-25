import os

from shared.src.core.settings import get_settings
from shared.src.enums import LanguageEnum, ImageFormat
from shared.src.services import BlurhashService, FileManagementService, TranslationService, ImageService
from shared.src.tables.food.dish_table import DishImageTable, DishTable, DishTranslationTable

from data_fetcher.src.core.services.image_generation_service import ImageGenerationService
from data_fetcher.src.core.services.remove_background_service import RemoveBackgroundService


class DishImageService:
    def __init__(self):
        self.settings = get_settings()
        self.remove_background_service = RemoveBackgroundService()
        self.image_generation_service = ImageGenerationService()
        self.translation_service = TranslationService()
        self.file_management_service = FileManagementService("shared/src/assets/dishes")
        self.image_service = ImageService()
        self.prompt_prefix = "Simplified 3D"
        
    def _generate_image_with_transparent_background(self, prompt: str, filename: str):
        image_path = self.image_generation_service.generate_image(prompt, height=512, width=512, steps=12, scales=5, seed=12345)
        image_path = self.remove_background_service.remove_background(image_path)
        return self.file_management_service.save_file_from_path(image_path, filename=filename)
    
    def _generate_image_url(self, filepath: str) -> str:
        filename = os.path.basename(filepath)
        return f"{self.settings.IMAGES_BASE_URL_DISHES}/{filename}"
    
    def generate_dish_image_table(self, dish_obj: DishTable) -> DishImageTable:
        dish_translation : DishTranslationTable = self.translation_service.get_translation(dish_obj, LanguageEnum.ENGLISH_US)
        dish_translation_title = dish_translation.title
        file_name = FileManagementService.generate_save_file_name(dish_translation_title)
        generated_image_path = self._generate_image_with_transparent_background(f"{self.prompt_prefix} {dish_translation_title}", f"{file_name}-{dish_obj.id}.png")
        image_path = self.image_service.convert_image(generated_image_path, ImageFormat.WEBP)
        image_path = self.image_service.resize_image(image_path, max_size=(48*6, 48*6))
        
        self.file_management_service.delete_file(generated_image_path)
        return DishImageTable(
            dish_id=dish_obj.id,
            url=self._generate_image_url(image_path),
            name=dish_translation_title,
            blurhash=BlurhashService.encode_image(image_path),
        )

if __name__ == "__main__":
    def main():
        service = DishImageService()
        dish_obj = DishTable(
            id="1",
            dish_type="main",
            dish_category="dessert",
            labels=["vanille pudding", "strawberry sauce"],
            translations=[DishTranslationTable(
                dish_id="1", 
                language=LanguageEnum.ENGLISH_US, 
                title="Vanille pudding with strawberry sauce")]
        )
        dish_image_table : DishImageTable = service.generate_dish_image_table(dish_obj)
        
        print(dish_image_table.url)
        print(dish_image_table.blurhash)
        print(dish_image_table.name)
        
    main()