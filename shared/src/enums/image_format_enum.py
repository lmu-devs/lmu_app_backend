import os
from enum import Enum


class ImageFormatEnum(Enum):
    PNG = "PNG"
    WEBP = "WEBP"
    JPEG = "JPEG"
    JPG = "JPG"

    @property
    def extension(self) -> str:
        """Returns the lowercase file extension"""
        return self.value.lower()

    @classmethod
    def from_filename(cls, filename: str) -> "ImageFormatEnum":
        """Get format from filename extension"""
        ext = os.path.splitext(filename)[1].upper().lstrip(".")
        try:
            return cls(ext)
        except ValueError:
            raise ValueError(f"Unsupported image format: {ext}")
