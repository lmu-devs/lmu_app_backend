from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declared_attr

class LanguageTable:
    """
    Abstract base class for language translations.
    Declares a language and a translation column.
    """
    __abstract__ = True
    
    @declared_attr
    def language(cls):
        return Column(String, primary_key=True)
    
     