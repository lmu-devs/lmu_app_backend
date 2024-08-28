# router should establish endpoints fot:
# 1. 


from fastapi import APIRouter, Depends

from api.database import get_db


router = APIRouter()


# Gets dish data
@router.get("/dishes/{dish_id}", response_model=dict)
async def get_dish(dish_id: str, Session = Depends(get_db)):
    pass


# Gets list of multiple canteens where dish is available in past and future dates
@router.get("/dishes/{dish_id}/dates", response_model=dict)
async def get_dish(dish_id: str, Session = Depends(get_db)):
    pass




