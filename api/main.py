from fastapi import FastAPI
from api.routers.fastapi import canteen_router
from api.routers.fastapi import menu_router
from api.routers.fastapi import dish_router

from api.database import init_db


def create_app():
    app = FastAPI(title="lmu-eat-api", description="API for canteen and menu data from munich.", version="0.1.0")
    
    # Include routers
    app.include_router(canteen_router.router,   prefix="/eat-api/v1", tags=["canteen"])
    app.include_router(menu_router.router,      prefix="/eat-api/v1", tags=["menu"])
    app.include_router(dish_router.router,      prefix="/eat-api/v1", tags=["dish"])

    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    # Initialize the database
    session = init_db()

    return app


def main():
    print("Running main()...")
    return create_app()

app = main()  # This line is crucial
