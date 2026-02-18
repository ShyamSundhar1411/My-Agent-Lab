import hashlib
from typing import Any, Dict, Optional

from src.shared.knowledge.config import graph_kg_client


class GraphStoreClient:
    def __init__(self, collection_name: Optional[str] = None):
        """
        Initialize graph store client

        Args:
            collection_name: Optional namespace for the collection (used as label prefix)
        """
        self.graph_client = graph_kg_client
        self.collection_name = collection_name
        self._label_prefix = f"{collection_name}_" if collection_name else ""

    def _label(self, name: str) -> str:
        return f"{self._label_prefix}{name}"

    def _id(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def query(self, cypher_query: str, params: Dict[str, Any] = None):
        return self.graph_client.query(cypher_query, params)

    def upsert_node(self, label: str, node_id: str, props: Dict[str, Any]):
        query = f"""
        MERGE (n:{self._label(label)}  {{id: $id}})
        SET n += $props
        """
        self.query(query, params={"id": node_id, "props": props})

    def upsert_relation(
        self,
        from_label: str,
        from_id: str,
        to_label: str,
        to_id: str,
        relation_type: str,
        props: Dict[str, Any] = None,
    ):
        query = f"""
        MATCH (a:{self._label(from_label)} {{id: $from_id}})
        MATCH (b:{self._label(to_label)} {{id: $to_id}})
        MERGE (a)-[r:{relation_type}]->(b)
        {"SET r += $props" if props else ""}
        """
        self.query(
            query, params={"from_id": from_id, "to_id": to_id, "props": props or {}}
        )
