from src.shared.knowledge.stores.graph_store import GraphStoreClient
import logging

logger = logging.getLogger(__name__)


class StoreService:
    def __init__(self, collection_name: str):
        """
        Initialize the service for a specific collection
        """
        self.store = GraphStoreClient(collection_name=collection_name)
        logger.info(f"StoreService initialized for collection: {collection_name}")

    def delete_collection(self):
        """
        Delete the collection and all its nodes/relations
        """
        try:
            logger.info(f"Deleting collection: {self.store.collection_name}")
            self.store.delete_collection()
            logger.info(
                f"Collection '{self.store.collection_name}' deleted successfully"
            )
            return {
                "status": "success",
                "message": f"Collection '{self.store.collection_name}' deleted",
            }
        except Exception as e:
            logger.exception(
                f"Failed to delete collection '{self.store.collection_name}' | Error: {e}"
            )
            return {"status": "error", "message": str(e)}
