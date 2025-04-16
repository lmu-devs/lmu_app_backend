from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.ext.declarative import declared_attr

from shared.src.core.database import Base


class LanguageTable(Base):
    """
    Abstract base class for language translations.
    Declares a language and a translation column.
    """

    __abstract__ = True

    @declared_attr
    def language(cls):
        return Column(String, primary_key=True)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now())

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now())
