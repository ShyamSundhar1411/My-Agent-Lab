import logging
from typing import Optional
import json
import io
from src.shared.knowledge.stores.graph_store import GraphStoreClient
from src.shared.knowledge.utils.chunking import split_data
import pdfplumber
from src.shared.llm.client import llm_client


logger = logging.getLogger(__name__)


class IngestService:
    def __init__(self):
        self.store = GraphStoreClient(collection_name="kg")
        self.text_splitter = split_data
        self.vector_index_created = False

    async def ingest_file_content(
        self, content: bytes, filename: str, source: Optional[str] = None
    ):
        """
        Detect file type by extension and ingest content accordingly
        """
        source = source or filename
        if filename.endswith(".json"):
            data = json.loads(content.decode("utf-8"))
            await self._ingest_json(data, source)
        elif filename.endswith(".pdf"):
            text = self._extract_pdf_text(content)
            await self._ingest_text_content(text, source)
        elif filename.endswith(".txt"):
            text = content.decode("utf-8")
            await self._ingest_text_content(text, source)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    async def _ensure_vector_index(
        self, node_label="Chunk", vector_property="textEmbedding", dim=1536
    ):
        if not self.vector_index_created:
            self.store.create_vector_index(
                index_name=f"{node_label}_vector_index",
                node_label=node_label,
                vector_property=vector_property,
                dimensions=dim,
            )
            self.vector_index_created = True

    async def _ingest_json(self, data: dict, source: str):
        chunks = self.text_splitter(data, source_name=source)

        doc_id = self.store._id(source)
        self.store.upsert_node(
            "Document", doc_id, {"title": source, "type": "json_document"}
        )

        await self._ensure_vector_index(node_label="Chunk")

        for chunk_data in chunks:
            chunk_id = chunk_data["chunkId"]
            text = chunk_data["text"]

            embedding = await llm_client.embed_text(text)

            self.store.upsert_node(
                "Chunk",
                chunk_id,
                {
                    "text": text,
                    "textEmbedding": embedding,
                    "formItem": chunk_data.get("formItem"),
                    "chunkSeqId": chunk_data.get("chunkSeqId"),
                    "source": chunk_data.get("source"),
                },
            )

            self.store.upsert_relation(
                "Document", doc_id, "Chunk", chunk_id, "HAS_CHUNK"
            )

        logger.info(f"JSON ingestion complete | source={source} | chunks={len(chunks)}")

    async def _extract_pdf_text(self, content: bytes) -> str:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])

    async def _ingest_text_content(self, text: str, source: str):
        chunks = self.text_splitter({"text": text})
        doc_id = self.store._id(source)
        self.store.upsert_node(
            "Document", doc_id, {"title": source, "type": "text_document"}
        )

        self._ensure_vector_index(node_label="Chunk")

        for chunk_data in chunks:
            chunk_id = chunk_data["chunkId"]
            text = chunk_data["text"]

            embedding = llm_client.embed(text)

            self.store.upsert_node(
                "Chunk",
                chunk_id,
                {
                    "text": text,
                    "textEmbedding": embedding,
                    "chunkSeqId": chunk_data.get("chunkSeqId"),
                    "source": source,
                },
            )

            self.store.upsert_relation(
                "Document", doc_id, "Chunk", chunk_id, "HAS_CHUNK"
            )

        logger.info(f"Text ingestion complete | source={source} | chunks={len(chunks)}")
