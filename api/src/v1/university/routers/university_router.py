# TODO: Implement university router
# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# from shared.src.core.database import get_async_db

# from ..models.university_model import University
# from ..services.university_service import UniversityService


# router = APIRouter()


# @router.get("/faculties", response_model=University, description="Get university data")
# async def get_faculties(
#     db: AsyncSession = Depends(get_async_db),
# ):
#     university_service = UniversityService(db)
#     faculties = await university_service.get_faculties()
#     return faculties
