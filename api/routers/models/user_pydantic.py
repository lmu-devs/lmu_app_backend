from api.models.user_model import UserTable
from api.schemas.user_scheme import User


def user_to_pydantic(user: UserTable) -> User:
    return User(
        id=user.id,
        device_id=user.device_id,
        name=user.name,
        email=user.email,
        password=user.password,
        api_key=user.api_key,
        creation_date=user.creation_date
    )