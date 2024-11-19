from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declared_attr


class ImageTable:
    __abstract__ = True
    
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True, index=True)
        
    @declared_attr
    def url(cls):
        return Column(String, nullable=False)
        
    @declared_attr
    def name(cls):
        return Column(String, nullable=False) 