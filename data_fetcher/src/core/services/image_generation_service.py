# https://huggingface.co/spaces/ginipick/text3d

from gradio_client import Client


class ImageGenerationService:
    def __init__(self):
        self.client = Client("ginipick/text3d")

    def generate_image(
        self,
        prompt: str,
        height: int = 1024,
        width: int = 1024,
        steps: int = 8,
        scales: float = 3.5,
        seed: int = 623608,
    ):
        result = self.client.predict(
            height=height,
            width=width,
            steps=steps,
            scales=scales,
            prompt=prompt,
            seed=seed,
            api_name="/process_and_save_image",
        )
        return result


if __name__ == "__main__":
    service = ImageGenerationService()
    print(
        service.generate_image(
            "Delicious and Simplified 3D Pasta all'arrabiata placed in a pastel green pasta bowl, white background",
            height=512,
            width=512,
            steps=12,
            scales=3.5,
            seed=123456,
        )
    )
