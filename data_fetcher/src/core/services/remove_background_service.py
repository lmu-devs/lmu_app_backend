# https://huggingface.co/spaces/KenjieDec/RemBG

from gradio_client import Client, handle_file


class RemoveBackgroundService:
    def __init__(self):
        self.client = Client("KenjieDec/RemBG")

    def remove_background(self, image_url: str):
        result = self.client.predict(
            file=handle_file(image_url),
            mask="Default",
            model="u2net",
            x=3,
            y=3,
            api_name="/inference",
        )
        return result


if __name__ == "__main__":
    service = RemoveBackgroundService()
    print(
        service.remove_background(
            "/private/var/folders/wl/9gn5jspx0gz7w70qz0rnqxn00000gn/T/gradio/9b6bee0f82a6b297f02dc76dc45b5d266d85298270aa769f1dac5efe1506b2d1/image.webp"
        )
    )
