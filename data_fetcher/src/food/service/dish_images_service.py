import os

from data_fetcher.src.core.services.image_generation_service import (
    ImageGenerationService,
)
from data_fetcher.src.core.services.remove_background_service import (
    RemoveBackgroundService,
)
from shared.src.core.settings import get_settings
from shared.src.enums import ImageFormatEnum, LanguageEnum
from shared.src.services import (
    BlurhashService,
    FileManagementService,
    ImageService,
    TranslationService,
)
from shared.src.tables.food.dish_table import (
    DishImageTable,
    DishTable,
    DishTranslationTable,
)


class DishImageService:
    def __init__(self):
        self.settings = get_settings()
        self.remove_background_service = RemoveBackgroundService()
        self.image_generation_service = ImageGenerationService()
        self.translation_service = TranslationService()
        self.file_management_service = FileManagementService("shared/src/assets/dishes")
        self.image_service = ImageService()

    def _get_dish_prompt(self, dish_name: str, dish_type: str, labels: list[str]) -> str:
        prefix = "Delicious and Simplified 3D"

        def get_color(dish_type: str, labels: list[str]) -> str:
            if "MEAT" in labels or dish_type == "Fleisch":
                return "pastel red"
            if (
                "VEGAN" in labels
                or "VEGETARIAN" in labels
                or dish_type in ["Vegetarisch", "Vegan", "Vegetarisch/fleischlos"]
            ):
                return "pastel green"
            if "FISH" in labels or dish_type == "Fisch":
                return "pastel blue"
            return "beige white"

        def get_container(dish_type: str, labels: list[str]) -> str:
            if dish_type == "Dessert (Glas)":
                return f"in a cylindric glass"
            if dish_type in ["Studitopf", "Suppentopf", "Suppe"]:
                return f"in a {get_color(dish_type, labels)} soup bowl"
            if dish_type == "Wok":
                return f"in a {get_color(dish_type, labels)} soup bowl"
            if dish_type == "Pasta":
                return f"in a {get_color(dish_type, labels)} pasta bowl"
            if dish_type == "Pizza":
                return f"on a pure white background"

            return f"on a {get_color(dish_type, labels)} single dinnerware, white background"

        prompt = f"{prefix} {dish_name} placed {get_container(dish_type, labels)}"
        print(prompt)
        return prompt

    async def _generate_image_with_transparent_background(self, prompt: str, filename: str):
        image_path = await self.image_generation_service.generate_image(
            prompt, height=512, width=512, steps=12, scales=4.5, seed=12345
        )
        image_path = await self.remove_background_service.remove_background(image_path)
        return await self.file_management_service.save_file_from_path(image_path, filename=filename)

    def _generate_image_url(self, filepath: str) -> str:
        filename = os.path.basename(filepath)
        return f"{self.settings.IMAGES_BASE_URL_DISHES}/{filename}"

    async def generate_dish_image_table(self, dish_obj: DishTable) -> DishImageTable:
        dish_translation = next(
            (t for t in dish_obj.translations if t.language == LanguageEnum.ENGLISH_US),
            None,
        )
        if not dish_translation:
            raise ValueError(f"No English translation found for dish {dish_obj.id}")

        dish_translation_title = dish_translation.title
        file_name = FileManagementService.generate_save_file_name(dish_translation_title)
        prompt = self._get_dish_prompt(dish_translation_title, dish_obj.dish_type, dish_obj.labels)
        generated_image_path = await self._generate_image_with_transparent_background(
            prompt, f"{file_name}-{dish_obj.id}.png"
        )
        image_path = await self.image_service.convert_image(generated_image_path, ImageFormatEnum.WEBP)
        image_path = await self.image_service.resize_image(image_path, max_size=(48 * 6, 48 * 6))

        await self.file_management_service.delete_file(generated_image_path)
        return DishImageTable(
            dish_id=dish_obj.id,
            url=self._generate_image_url(image_path),
            name=dish_translation_title,
            blurhash=await BlurhashService.encode_image(image_path),
        )


if __name__ == "__main__":
    service = DishImageService()
    dish_obj = DishTable(
        id="1",
        dish_type="Studitopf",
        dish_category="dessert",
        labels=["MEAT"],
        translations=[DishTranslationTable(dish_id="1", language=LanguageEnum.ENGLISH_US, title="Chicken curry")],
    )
    dish_obj = DishTable(
        id="1",
        dish_type="Fisch",
        dish_category="dessert",
        labels=["FISH"],
        translations=[
            DishTranslationTable(
                dish_id="1",
                language=LanguageEnum.ENGLISH_US,
                title="Dill bites from matjes herring",
            )
        ],
    )
    dish_obj = DishTable(
        id="1",
        dish_type="Vegetarisch/fleischlos",
        dish_category="dessert",
        labels=["FISH"],
        translations=[
            DishTranslationTable(
                dish_id="1",
                language=LanguageEnum.ENGLISH_US,
                title="Three spinach dumplings with tomato sauce",
            )
        ],
    )
    dish_image_table: DishImageTable = service.generate_dish_image_table(dish_obj)

    print(dish_image_table.name)
    print(dish_image_table.url)
    print(dish_image_table.blurhash)
