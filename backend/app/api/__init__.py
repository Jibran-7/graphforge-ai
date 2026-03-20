from fastapi import APIRouter

from app.api.routes import documents_router, graph_router, health_router, query_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(documents_router)
api_router.include_router(graph_router)
api_router.include_router(query_router)
