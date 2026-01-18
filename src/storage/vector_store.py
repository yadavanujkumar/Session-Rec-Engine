"""Vector database for item embeddings and similarity search."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np
from typing import List, Tuple
import uuid


class VectorStore:
    """Qdrant-based vector store for item embeddings."""

    def __init__(self, host: str, port: int, collection_name: str, embedding_dim: int):
        """
        Initialize vector store.

        Args:
            host: Qdrant host
            port: Qdrant port
            collection_name: Name of the collection
            embedding_dim: Dimension of embeddings
        """
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim, distance=Distance.COSINE
                ),
            )

    def add_items(self, item_ids: List[str], embeddings: np.ndarray) -> None:
        """
        Add items with their embeddings to the vector store.

        Args:
            item_ids: List of item IDs
            embeddings: Item embeddings [num_items, embedding_dim]
        """
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={"item_id": item_id},
            )
            for item_id, embedding in zip(item_ids, embeddings)
        ]

        self.client.upsert(collection_name=self.collection_name, points=points)

    def search_similar(
        self, query_vector: np.ndarray, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Search for similar items based on query vector.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of (item_id, score) tuples
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=top_k,
        )

        return [(hit.payload["item_id"], hit.score) for hit in results]

    def health_check(self) -> bool:
        """Check if Qdrant is healthy."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
