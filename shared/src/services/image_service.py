import os
from typing import Optional

from PIL import Image

from shared.src.enums.image_format_enum import ImageFormatEnum


class ImageService:
    @staticmethod
    def _get_save_parameters(format: ImageFormatEnum, quality: Optional[int] = None) -> dict:
        """
        Get the appropriate save parameters for different image formats

        Args:
            format: The image format (PNG, WEBP, JPEG, etc.)
            quality: Optional quality setting (0-100)

        Returns:
            dict: Parameters to use with PIL's save method
        """
        save_params = {}
        if quality is not None:
            if format == ImageFormatEnum.PNG:
                save_params["optimize"] = True
            else:
                save_params["quality"] = quality

            if format == ImageFormatEnum.WEBP:
                save_params["method"] = 6  # Highest compression method for WebP

        return save_params

    @staticmethod
    def convert_image(
        input_path: str,
        output_format: ImageFormatEnum,
        quality: Optional[int] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Convert an image to a different format and optionally compress it

        Args:
            input_path: Path to the input image
            output_format: Desired output format (ImageFormat enum)
            quality: Quality setting (0-100, where 100 is best). Default is None (no compression)
            output_path: Optional custom output path. If None, uses input path with new extension
        """
        try:
            with Image.open(input_path) as img:
                # Convert RGBA to RGB if saving as JPEG
                if output_format in [ImageFormatEnum.JPEG, ImageFormatEnum.JPG] and img.mode == "RGBA":
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background

                # Generate output path if not provided
                if output_path is None:
                    directory = os.path.dirname(input_path)
                    filename = os.path.splitext(os.path.basename(input_path))[0]
                    output_path = os.path.join(directory, f"{filename}.{output_format.extension}")

                # Get save parameters
                save_params = ImageService._get_save_parameters(output_format, quality)
                img.save(output_path, output_format.value, **save_params)
                return output_path

        except Exception as e:
            raise Exception(f"Failed to convert image: {str(e)}")

    @staticmethod
    def compress_image(input_path: str, quality: int, output_path: Optional[str] = None) -> str:
        """
        Compress an image while maintaining its original format

        Args:
            input_path: Path to the input image
            quality: Quality setting (0-100, where 100 is best)
            output_path: Optional custom output path. If None, overwrites input file

        Returns:
            str: Path to the compressed image
        """
        try:
            # Get original format
            with Image.open(input_path) as img:
                format = ImageFormatEnum(img.format)  # Convert string to ImageFormat enum
                return ImageService.convert_image(
                    input_path=input_path,
                    output_format=format,
                    quality=quality,
                    output_path=output_path,
                )
        except Exception as e:
            raise Exception(f"Failed to compress image: {str(e)}")

    @staticmethod
    def resize_image(
        input_path: str,
        max_size: tuple[int, int],
        output_path: Optional[str] = None,
        quality: Optional[int] = None,
    ) -> str:
        """
        Resize an image while maintaining aspect ratio

        Args:
            input_path: Path to the input image
            max_size: Tuple of (max_width, max_height)
            output_path: Optional custom output path. If None, uses input path with _resized suffix
            quality: Optional quality setting (0-100) for compression
        """
        try:
            format = ImageFormatEnum.from_filename(input_path)

            with Image.open(input_path) as img:
                # Calculate new size maintaining aspect ratio
                original_width, original_height = img.size
                max_width, max_height = max_size

                # Calculate ratios
                width_ratio = max_width / original_width
                height_ratio = max_height / original_height

                # Use the smaller ratio to ensure image fits within max dimensions
                ratio = min(width_ratio, height_ratio)

                # Calculate new dimensions
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)

                # Only resize if image is larger than max dimensions
                if ratio < 1:
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Generate output path if not provided
                if output_path is None:
                    directory = os.path.dirname(input_path)
                    filename = os.path.splitext(os.path.basename(input_path))[0]
                    output_path = os.path.join(directory, f"{filename}.{format.extension}")

                # Get save parameters
                save_params = ImageService._get_save_parameters(format, quality)
                img.save(output_path, format.value, **save_params)
                return output_path

        except Exception as e:
            raise Exception(f"Failed to resize image: {str(e)}")


if __name__ == "__main__":
    service = ImageService()

    # Convert PNG to WebP with compression
    # result = service.convert_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.png",
    #     output_format=ImageFormat.WEBP,
    #     quality=30,
    #     output_path="shared/src/assets/dishes/Vanille_pudding_30.webp"
    # )
    # result = service.convert_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.png",
    #     output_format=ImageFormat.WEBP,
    #     quality=40,
    #     output_path="shared/src/assets/dishes/Vanille_pudding_40.webp"
    # )
    # result = service.convert_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.png",
    #     output_format=ImageFormat.WEBP,
    #     quality=50,
    #     output_path="shared/src/assets/dishes/Vanille_pudding_50.webp"
    # )
    # result = service.convert_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.png",
    #     output_format=ImageFormat.WEBP,
    #     quality=60,
    #     output_path="shared/src/assets/dishes/Vanille_pudding_60.webp"
    # )
    # result = service.convert_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.png",
    #     output_format=ImageFormat.WEBP,
    #     quality=70,
    #     output_path="shared/src/assets/dishes/Vanille_pudding_70.webp"
    # )
    # result = service.convert_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.png",
    #     output_format=ImageFormat.WEBP,
    #     quality=80,
    #     output_path="shared/src/assets/dishes/Vanille_pudding_80.webp"
    # )
    # result = service.convert_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.png",
    #     output_format=ImageFormat.WEBP,
    #     quality=90,
    #     output_path="shared/src/assets/dishes/Vanille_pudding_90.webp"
    # )
    # print(f"Converted image saved to: {result}")

    # Just compress an existing image
    # result = service.compress_image(
    #     input_path="shared/src/assets/dishes/Vanille_pudding_with_strawberry_sauce-1 copy.webp",
    #     quality=50
    # )
    # print(f"Compressed image saved to: {result}")

    # Resize and save to specific location
    i = 90
    result = service.resize_image(
        input_path=f"shared/src/assets/dishes/Vanille_pudding_{i}.webp",
        max_size=(48 * 4, 48 * 4),
        quality=i,
        output_path=f"shared/src/assets/dishes/Vanille_pudding_{i}_resized.webp",
    )
    # print(f"Resized image saved to: {result}")
