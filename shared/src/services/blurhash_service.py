import blurhash


class BlurhashService:
    @staticmethod
    def encode_image(image_path: str, x_components: int = 4, y_components: int = 4) -> str:
        """
        Encode an image file to blurhash string.

        Args:
            image_path: Path to the image file
            x_components: Number of X components for blurhash (default: 4)
            y_components: Number of Y components for blurhash (default: 4)

        Returns:
            str: Blurhash string representation of the image
        """
        with open(image_path, "rb") as image_file:
            return blurhash.encode(image_file, x_components=x_components, y_components=y_components)
