from shared.src.tables import UserTable

from ..schemas.user_scheme import User


def user_to_pydantic(user: UserTable) -> User:
    return User(
        id=user.id,
        device_id=user.device_id,
        name=user.name,
        email=user.email,
        password=user.password,
        api_key=user.api_key,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
