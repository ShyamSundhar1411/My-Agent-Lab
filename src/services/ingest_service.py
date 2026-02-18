import logging
from typing import Any, Dict

from src.shared.knowledge.stores.graph_store import GraphStoreClient

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(self):
        self.store = GraphStoreClient(collection_name="kg")
        logger.info("IngestService initialized")

    def ingest_json(self, data: Dict[str, Any], source: str):
        logger.info(f"Starting JSON ingestion | source={source}")

        try:
            json_type = self._detect_json_type(data)
            logger.info(f"JSON type detected | type={json_type} | source={source}")

            if json_type == "document":
                self._ingest_document_json(data, source)

            elif json_type == "structured":
                self._ingest_structured_json(data, source)

            else:
                self._ingest_generic_json(data, source)

            logger.info(f"JSON ingestion completed successfully | source={source}")

        except Exception as e:
            logger.exception(f"JSON ingestion failed | source={source} | error={e}")
            raise

    def _detect_json_type(self, data: Dict[str, Any]) -> str:
        logger.debug("Detecting JSON type")

        long_text_fields = 0
        for v in data.values():
            if isinstance(v, str) and len(v) > 300:
                long_text_fields += 1

        if long_text_fields >= 1:
            logger.debug("Detected document-style JSON")
            return "document"

        if all(not isinstance(v, str) or len(v) < 200 for v in data.values()):
            logger.debug("Detected structured JSON")
            return "structured"

        logger.debug("Detected generic JSON")
        return "generic"

    def _ingest_document_json(self, data: Dict[str, Any], source: str):
        logger.info(f"Ingesting document JSON | source={source}")

        doc_id = self.store._id(source)

        self.store.upsert_node(
            "Document", doc_id, {"title": source, "type": "json_document"}
        )

        logger.debug(f"Document node created | doc_id={doc_id}")

        for key, value in data.items():
            logger.debug(f"Processing section | section={key}")

            if key.lower() in ["source", "author", "origin", "created_at"]:
                meta_id = self.store._id(str(value))

                self.store.upsert_node(
                    "Metadata", meta_id, {"key": key, "value": str(value)}
                )

                self.store.upsert_relation(
                    "Document", doc_id, "Metadata", meta_id, "HAS_METADATA"
                )

                logger.debug(f"Metadata linked | key={key}")
                continue

            section_id = self.store._id(f"{doc_id}:{key}")

            self.store.upsert_node("Section", section_id, {"name": key})

            self.store.upsert_relation(
                "Document", doc_id, "Section", section_id, "HAS_SECTION"
            )

            logger.debug(f"Section created | section={key} | section_id={section_id}")

            if isinstance(value, str):
                chunks = self._chunk_text(value)
                logger.debug(f"Chunking section | section={key} | chunks={len(chunks)}")

                for i, chunk in enumerate(chunks):
                    chunk_id = self.store._id(f"{section_id}:{i}")

                    self.store.upsert_node(
                        "Chunk", chunk_id, {"text": chunk, "index": i}
                    )

                    self.store.upsert_relation(
                        "Section", section_id, "Chunk", chunk_id, "HAS_CHUNK"
                    )

        logger.info(f"Document JSON ingestion done | source={source}")

    def _ingest_structured_json(self, data: Dict[str, Any], source: str):
        logger.info(f"Ingesting structured JSON | source={source}")

        root_id = self.store._id(source)

        self.store.upsert_node(
            "StructuredDocument", root_id, {"source": source, "type": "structured_json"}
        )

        logger.debug(f"Structured root node created | root_id={root_id}")

        self._walk_structure(data, root_id, "StructuredDocument")

        logger.info(f"Structured JSON ingestion done | source={source}")

    def _ingest_generic_json(self, data: Dict[str, Any], source: str):
        logger.info(f"Ingesting generic JSON | source={source}")

        root_id = self.store._id(source)

        self.store.upsert_node("GenericJSON", root_id, {"source": source})

        logger.debug(f"Generic root node created | root_id={root_id}")

        self._walk_structure(data, root_id, "GenericJSON")

        logger.info(f"Generic JSON ingestion done | source={source}")

    def _walk_structure(self, obj: Any, parent_id: str, parent_label: str):
        if isinstance(obj, dict):
            for k, v in obj.items():
                node_id = self.store._id(f"{parent_id}:{k}")

                self.store.upsert_node("Node", node_id, {"name": k})

                self.store.upsert_relation(
                    parent_label, parent_id, "Node", node_id, "HAS_NODE"
                )

                logger.debug(f"Node created | key={k} | node_id={node_id}")

                self._walk_structure(v, node_id, "Node")

        elif isinstance(obj, list):
            for item in obj:
                self._walk_structure(item, parent_id, parent_label)

        else:
            val_id = self.store._id(str(obj))

            self.store.upsert_node("Value", val_id, {"value": str(obj)})

            self.store.upsert_relation(
                parent_label, parent_id, "Value", val_id, "HAS_VALUE"
            )

            logger.debug(f"Value node created | value={obj}")

    def _chunk_text(self, text: str, size: int = 800):
        chunks = [text[i : i + size] for i in range(0, len(text), size)]
        logger.debug(f"Text chunked | total_chunks={len(chunks)}")
        return chunks
