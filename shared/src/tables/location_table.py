from sqlalchemy import Column, Float, String
from sqlalchemy.ext.declarative import declared_attr


class LocationTable:
    """
    Abstract base class for location.
    Declares a location column.
    """
    __abstract__ = True
    
    @declared_attr
    def address(cls):
        return Column(String, primary_key=True)
    
    @declared_attr
    def latitude(cls):
        return Column(Float, nullable=True)
    
    @declared_attr
    def longitude(cls):
        return Column(Float, nullable=True)