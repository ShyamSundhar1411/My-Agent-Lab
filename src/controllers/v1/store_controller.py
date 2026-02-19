from fastapi import APIRouter, Depends, Path, HTTPException
from src.services.store_service import StoreService
import logging


logger = logging.getLogger(__name__)
store_router = APIRouter(tags=["stores"])


def get_store_service(collection_name: str) -> StoreService:
    return StoreService(collection_name=collection_name)


logger = logging.getLogger(__name__)
store_router = APIRouter(tags=["stores"])


@store_router.delete("/store/graph/collections/{collection_name}")
def delete_collection(
    collection_name: str = Path(..., description="Name of the collection to delete"),
    store_service: StoreService = Depends(get_store_service),
):
    """
    Delete a collection using the StoreService dependency
    """
    result = store_service.delete_collection()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result
