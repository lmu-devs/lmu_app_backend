
from api.models.user_model import UserDto, UserTable


def user_to_pydantic(user: UserTable) -> UserDto:
    return UserDto(
        id=user.id,
        device_id=user.device_id,
        name=user.name,
        email=user.email,
        password=user.password,
        api_key=user.api_key,
        creation_date=user.creation_date
    )