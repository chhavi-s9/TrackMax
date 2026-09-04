from app.routes.assets import router as assets_router
from app.routes.blocks import router as blocks_router
from app.routes.departments import router as departments_router
from app.routes.maintenance import router as maintenance_router
from app.routes.optimizer import router as optimizer_router
from app.routes.overview import router as overview_router
from app.routes.prioritization import router as prioritization_router
from app.routes.resources import router as resources_router
from app.routes.scenarios import router as scenarios_router
from app.routes.schedules import router as schedules_router
from app.routes.trains import router as trains_router
from app.routes.weather import router as weather_router

ALL_ROUTERS = [
    departments_router,
    assets_router,
    maintenance_router,
    resources_router,
    trains_router,
    schedules_router,
    blocks_router,
    overview_router,
    prioritization_router,
    optimizer_router,
    scenarios_router,
    weather_router,
]
