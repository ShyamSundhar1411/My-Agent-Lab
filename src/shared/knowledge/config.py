import logging
from typing import Optional

from langchain_neo4j import Neo4jGraph

from src.core.config import settings

logger = logging.getLogger(__name__)


class Neo4JGraphClient:
    """Singleton LangChain Neo4j connection manager"""

    def __init__(
        self,
        uri: str = settings.NEO4J_URI,
        username: str = settings.NEO4J_USERNAME,
        password: str = settings.NEO4J_PASSWORD,
        database: str = settings.NEO4J_DATABASE,
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._graph: Optional[Neo4jGraph] = None

    def initialize(self) -> Neo4jGraph:
        if self._graph is None:
            logger.info(f"Initializing LangChain Neo4j connection to {self.uri}")
            self._graph = Neo4jGraph(
                url=self.uri,
                username=self.username,
                password=self.password,
                database=self.database,
            )

            logger.info("LangChain Neo4j connection initialized successfully")

    def close(self):
        """Close Neo4j connection"""
        if self._graph is not None:
            logger.info("Closing LangChain Neo4j connection")
            self._graph = None

    def get_graph(self) -> Neo4jGraph:
        if self._graph is None:
            self.initialize()
        return self._graph

    def refresh_schema(self):
        graph = self.get_graph()
        graph.refresh_schema()
        logger.info("Neo4j schema refreshed")

    def get_schema(self) -> str:
        """Get graph schema"""
        graph = self.get_graph()
        return graph.schema

    def health_check(self) -> bool:
        """Check if Neo4j connection is healthy"""
        try:
            graph = self.get_graph()
            graph.query("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

    def query(self, cypher_query: str, params: dict = None):
        graph = self.get_graph()
        return graph.query(cypher_query, params)


graph_kg_client = Neo4JGraphClient()
graph_kg_client.initialize()
