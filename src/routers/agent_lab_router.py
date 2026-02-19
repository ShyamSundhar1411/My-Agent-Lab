from fastapi import APIRouter

from src.controllers.health_controller import health_router
from src.controllers.v1.ingest_controller import ingestion_router as ingestion_router_v1
from src.controllers.v1.store_controller import store_router as store_router_v1

v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v1_router.include_router(ingestion_router_v1)
v1_router.include_router(store_router_v1)
agent_lab_router = APIRouter()
agent_lab_router.include_router(v1_router)

agent_lab_router.include_router(health_router, tags=["health"])
