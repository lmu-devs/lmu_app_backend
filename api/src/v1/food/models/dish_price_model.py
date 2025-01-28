from typing import List
from pydantic import BaseModel, RootModel

from shared.src.tables import DishPriceTable


class DishPrice(BaseModel):
    category: str
    base_price: float
    price_per_unit: float
    unit: str
    
    @classmethod
    def from_table(cls, price: DishPriceTable) -> 'DishPrice':
        return DishPrice(
            category=price.category,
            base_price=price.base_price or 0,
            price_per_unit=price.price_per_unit or 0,
            unit=price.unit or "None"
        )
        
class DishPrices(RootModel):
    root: List[DishPrice]
    
    @classmethod
    def from_table(cls, prices: List[DishPriceTable]) -> 'DishPrices':
        return DishPrices(root=[DishPrice.from_table(price) for price in prices])