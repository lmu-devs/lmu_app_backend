from sqlalchemy import ARRAY, Column, String, JSON
from sqlalchemy.ext.declarative import declared_attr

from shared.src.core.database import Base


class LinkTableV2(Base):
    __abstract__ = True
    
    @declared_attr
    def id(cls):
        return Column(String, primary_key=True)
    
    @declared_attr
    def url(cls):
        return Column(String, nullable=False)
    
    @declared_attr
    def favicon_url(cls):
        return Column(String, nullable=True)
    
    @declared_attr
    def title(cls):
        return Column(String, nullable=False)
    
    @declared_attr
    def description(cls):
        return Column(String, nullable=True)
    
    @declared_attr
    def aliases(cls):
        return Column(JSON, nullable=True, default=list)