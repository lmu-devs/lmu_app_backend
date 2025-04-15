import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr


class ImageTable:
    __abstract__ = True

    @declared_attr
    def id(cls):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    @declared_attr
    def url(cls):
        return Column(String, nullable=False)

    @declared_attr
    def blurhash(cls):
        return Column(String, nullable=True)

    @declared_attr
    def name(cls):
        return Column(String, nullable=False)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now())

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now())
