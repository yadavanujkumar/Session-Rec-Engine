"""Recommendation service that orchestrates all components."""

import torch
from typing import List, Optional, Tuple
from src.models import SASRec
from src.storage import SessionStore, VectorStore
from src.coldstart import ColdStartHandler
from src.monitoring import MetricsTracker, LatencyTimer
from src.utils import ItemCatalog


class RecommendationService:
    """Main recommendation service."""

    def __init__(
        self,
        model: SASRec,
        session_store: SessionStore,
        vector_store: VectorStore,
        coldstart_handler: ColdStartHandler,
        metrics_tracker: MetricsTracker,
        item_catalog: ItemCatalog,
        sequence_length: int = 5,
        top_k: int = 5,
    ):
        """
        Initialize recommendation service.

        Args:
            model: SASRec model
            session_store: Session store
            vector_store: Vector store
            coldstart_handler: Cold-start handler
            metrics_tracker: Metrics tracker
            item_catalog: Item catalog
            sequence_length: Maximum sequence length
            top_k: Number of recommendations to return
        """
        self.model = model
        self.session_store = session_store
        self.vector_store = vector_store
        self.coldstart_handler = coldstart_handler
        self.metrics_tracker = metrics_tracker
        self.item_catalog = item_catalog
        self.sequence_length = sequence_length
        self.top_k = top_k
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def add_click_event(self, session_id: str, item_id: str) -> None:
        """
        Add a click event to a session.

        Args:
            session_id: Session identifier
            item_id: Item that was clicked
        """
        self.session_store.add_click(session_id, item_id)

    def get_recommendations(self, session_id: str) -> Tuple[List[str], bool]:
        """
        Get recommendations for a session.

        Args:
            session_id: Session identifier

        Returns:
            Tuple of (list of recommended item IDs, whether cold-start was used)
        """
        with LatencyTimer() as timer:
            # Get session data
            session_length = self.session_store.get_session_length(session_id)

            # Check if cold-start is needed
            if self.coldstart_handler.should_use_coldstart(session_length):
                recommendations = self.coldstart_handler.get_recommendations(self.top_k)
                used_coldstart = True
            else:
                # Use model for recommendations
                recommendations = self._get_model_recommendations(session_id)
                used_coldstart = False

        # Record metrics
        self.metrics_tracker.record_recommendation(
            items_recommended=recommendations,
            latency_ms=timer.latency_ms,
            used_coldstart=used_coldstart,
        )

        return recommendations, used_coldstart

    def _get_model_recommendations(self, session_id: str) -> List[str]:
        """
        Get recommendations using the model.

        Args:
            session_id: Session identifier

        Returns:
            List of recommended item IDs
        """
        # Get item sequence
        item_ids = self.session_store.get_item_sequence(
            session_id, self.sequence_length
        )

        if not item_ids:
            # Fallback to cold-start if no items
            return self.coldstart_handler.get_recommendations(self.top_k)

        # Convert to indices
        item_indices = [
            self.item_catalog.get_item_index(item_id) for item_id in item_ids
        ]

        # Pad sequence if needed
        if len(item_indices) < self.sequence_length:
            item_indices = [0] * (
                self.sequence_length - len(item_indices)
            ) + item_indices
        else:
            item_indices = item_indices[-self.sequence_length :]

        # Convert to tensor
        item_seq = torch.tensor([item_indices], dtype=torch.long).to(self.device)

        # Get predictions
        with torch.no_grad():
            top_items, top_scores = self.model.predict_next_items(
                item_seq, top_k=self.top_k
            )

        # Convert indices back to item IDs
        top_items_np = top_items.cpu().numpy()[0]
        recommendations = [
            self.item_catalog.get_item_id(int(idx)) for idx in top_items_np
        ]

        # Filter out unknown items
        recommendations = [
            item_id for item_id in recommendations if item_id != "unknown"
        ]

        # If we don't have enough recommendations, supplement with cold-start
        if len(recommendations) < self.top_k:
            coldstart_recs = self.coldstart_handler.get_recommendations(self.top_k)
            for rec in coldstart_recs:
                if rec not in recommendations:
                    recommendations.append(rec)
                if len(recommendations) >= self.top_k:
                    break

        return recommendations[: self.top_k]

    def record_feedback(
        self,
        session_id: str,
        recommended_items: List[str],
        clicked_item: Optional[str] = None,
    ):
        """
        Record user feedback for recommendations.

        Args:
            session_id: Session identifier
            recommended_items: Items that were recommended
            clicked_item: Item that was clicked (if any)
        """
        # Update metrics
        self.metrics_tracker.record_recommendation(
            items_recommended=recommended_items, item_clicked=clicked_item
        )

        # Update cold-start bandit
        for item_id in recommended_items:
            clicked = clicked_item == item_id
            self.coldstart_handler.update_feedback(item_id, clicked)

    def health_check(self) -> dict:
        """
        Check health of all components.

        Returns:
            Dictionary with health status
        """
        return {
            "session_store": self.session_store.health_check(),
            "vector_store": self.vector_store.health_check(),
            "model": self.model is not None,
        }
