from fastapi import FastAPI
from api.routers.api import canteen_router
from api.routers.api import menu_router
from api.routers.api import dish_router


def create_app():
    app = FastAPI(title="lmu-eat-api", description="API for canteen and menu data from munich.", version="0.1.0")
    


    # Include routers
    app.include_router(canteen_router.router,   prefix="/eat-api/v1", tags=["canteen"])
    app.include_router(menu_router.router,      prefix="/eat-api/v1", tags=["menu"])
    app.include_router(dish_router.router,      prefix="/eat-api/v1", tags=["dish"])

    @app.get("/")
    async def root():
        return {"message": "Hello World"}


    return app


def main():
    print("Running main()...")
    return create_app()

app = main()  # This line is crucial
