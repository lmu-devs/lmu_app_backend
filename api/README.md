# LMU App API Service

The API service is built with FastAPI and provides the backend endpoints for the LMU App. It follows a modular structure with versioned endpoints and domain-specific modules.

## Table of Contents
- [LMU App API Service](#lmu-app-api-service)
  - [Table of Contents](#table-of-contents)
  - [Structure](#structure)
  - [Modules](#modules)
  - [Development](#development)
    - [Local Setup](#local-setup)
    - [Code Style](#code-style)
  - [Testing](#testing)
  - [API Documentation](#api-documentation)
    - [Rate Limiting](#rate-limiting)
  - [Service Structure](#service-structure)
    - [Core Components](#core-components)
      - [Authentication (api\_key.py)](#authentication-api_keypy)
      - [Language Support (language.py)](#language-support-languagepy)
      - [Generic Services](#generic-services)
        - [Like Service](#like-service)
    - [Module Structure](#module-structure)
      - [1. Models](#1-models)
      - [2. Router](#2-router)
      - [3. Service](#3-service)
    - [Best Practices](#best-practices)

## Structure

```
api/
├── src/
│   ├── v1/                # API Version 1
│   │   ├── core/          # Core functionality and utilities
│   │   ├── food/          # Food service endpoints
│   │   ├── cinema/        # Cinema information endpoints
│   │   ├── feedback/      # User feedback endpoints
│   │   ├── home/          # Home screen endpoints
│   │   ├── link/          # External links management
│   │   ├── log/           # Logging and monitoring
│   │   ├── places/        # Places and locations
│   │   ├── roomfinder/    # Room finding service
│   │   ├── sport/         # Sports facilities and courses
│   │   ├── timeline/      # Event timeline
│   │   ├── user/          # User management
│   │   └── wishlist/      # User wishlist features
└── tests/                 # Test suite
```

## Modules

The API is organized into domain-specific modules:

- **Core**: Base functionality, middleware, and shared utilities
- **Food**: Cafeteria menus, food locations, and related services
- **Cinema**: Movie schedules, and cinema locations
- **Feedback**: User feedback and rating system
- **Home**: Home screen content and personalization
- **Link**: External resource management and deep linking
- **Log**: Application logging and monitoring
- **Places**: Location-based services and place information
- **Roomfinder**: Room search and navigation
- **Sport**: Sports facilities, course schedules, and bookings
- **Timeline**: Event management and timeline features
- **User**: User authentication, profiles, and preferences
- **Wishlist**: User wishlist and saved items

## Development

### Local Setup

1. Start the development server with hot-reload:
   ```bash
   docker compose up api_dev db --build
   ```

2. The API will be available at:
   - Local: http://localhost:8001
   - Development: http://api-staging.lmu-dev.org
   - Production: http://api.lmu-dev.org


### Code Style

- Follow PEP 8 guidelines
- Use async/await for database operations
- Document all endpoints with OpenAPI specifications
- Include type hints for all functions

## Testing

The test suite is located in the `tests/` directory. To run tests:

```bash
# Run in the api_dev container
pytest tests/
```

## API Documentation

When the server is running, documentation is available at:

- Swagger UI: `/v1/docs`


### Rate Limiting

There is no rate limiting in the API currently.

## Service Structure

The API follows a modular architecture with clear separation of concerns:

```
api/src/v1/
├── core/                   # Core functionality
│   ├── api_key.py         # API key authentication
│   ├── language.py        # Language handling
│   └── service/
│       └── like_service.py # Generic like functionality
├── {module}/              # Domain-specific modules
    ├── models/            # Pydantic models and schemas
    ├── router.py          # FastAPI router and endpoints
    ├── service.py         # Business logic
    └── dependencies.py    # Module-specific dependencies
```

### Core Components

#### Authentication (api_key.py)
The API uses API key authentication with three levels:
- **User API Key**: For authenticated user operations
- **System API Key**: For system operations (e.g., user creation)
- **Admin API Key**: For administrative operations

Example:
```python
from fastapi import Depends
from core.api_key import APIKey

@router.get("/protected")
async def protected_endpoint(user = Depends(APIKey.verify_user_api_key)):
    return {"user_id": user.id}
```

#### Language Support (language.py)
Built-in language handling through the Accept-Language header:
- Supports multiple languages via `LanguageEnum`
- Default fallback to German
- Easy integration as FastAPI dependency

Example:
```python
from core.language import get_language

@router.get("/localized")
async def localized_endpoint(language = Depends(get_language)):
    return {"message": messages[language]}
```

#### Generic Services

##### Like Service
Reusable like/unlike functionality for any entity:
- Generic methods for handling likes
- Automatic table name resolution
- Built-in error handling

Example:
```python
from core.service.like_service import LikeService

async def toggle_wishlist_like(wishlist_id: uuid.UUID, user_id: uuid.UUID):
    like_service = LikeService(db)
    return await like_service.toggle_like(WishlistLikeTable, wishlist_id, user_id)
```

### Module Structure

Each domain module follows this structure:

#### 1. Models
```python
# models/entity_model.py
from pydantic import BaseModel

class EntityCreate(BaseModel):
    name: str
    description: str

class EntityResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
```

#### 2. Router
```python
# router.py
from fastapi import APIRouter, Depends
from .service import EntityService
from .models.entity_model import EntityCreate, EntityResponse

router = APIRouter(prefix="/v1/entity")

@router.post("/", response_model=EntityResponse)
async def create_entity(
    data: EntityCreate,
    service: EntityService = Depends()
):
    return await service.create(data)
```

#### 3. Service
```python
# service.py
from sqlalchemy.ext.asyncio import AsyncSession
from shared.src.core.database import get_async_db

class EntityService:
    def __init__(self, db: AsyncSession = Depends(get_async_db)):
        self.db = db

    async def create(self, data: EntityCreate) -> EntityResponse:
        # Business logic here
        pass
```

### Best Practices

1. **Dependency Injection**
   - Use FastAPI's dependency injection system
   - Create reusable dependencies in `core/` or module's `dependencies.py`
   - Leverage dependency overrides for testing

2. **Service Layer**
   - Keep business logic in service classes
   - Use dependency injection for database sessions
   - Implement proper error handling and logging

3. **Models**
   - Use Pydantic models for request/response validation
   - Separate database models from API models
   - Include proper field validation and documentation

4. **Error Handling**
   - Use custom exceptions from `shared.src.core.exceptions`
   - Implement proper error logging
   - Return consistent error responses

5. **Database Operations**
   - Use async SQLAlchemy for database operations
   - Implement proper transaction handling
   - Use type hints for better code clarity
