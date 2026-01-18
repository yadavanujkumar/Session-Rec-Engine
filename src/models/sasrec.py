"""SASRec (Self-Attentive Sequential Recommendation) model implementation."""

import torch
import torch.nn as nn
from typing import Tuple


class SASRec(nn.Module):
    """Self-Attentive Sequential Recommendation model."""

    def __init__(
        self,
        num_items: int,
        embedding_dim: int = 128,
        num_heads: int = 4,
        num_layers: int = 2,
        dropout: float = 0.1,
        max_seq_len: int = 5,
    ):
        """
        Initialize SASRec model.

        Args:
            num_items: Number of items in catalog
            embedding_dim: Dimension of item embeddings
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
            dropout: Dropout rate
            max_seq_len: Maximum sequence length
        """
        super(SASRec, self).__init__()

        self.num_items = num_items
        self.embedding_dim = embedding_dim
        self.max_seq_len = max_seq_len

        # Item embeddings (0 is padding)
        self.item_embedding = nn.Embedding(num_items + 1, embedding_dim, padding_idx=0)

        # Positional embeddings
        self.positional_embedding = nn.Embedding(max_seq_len, embedding_dim)

        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=embedding_dim * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Output layer
        self.output_layer = nn.Linear(embedding_dim, num_items)

        # Layer normalization
        self.layer_norm = nn.LayerNorm(embedding_dim)

        # Dropout
        self.dropout = nn.Dropout(dropout)

    def forward(self, item_seq: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the model.

        Args:
            item_seq: Tensor of shape (batch_size, seq_len) containing item indices

        Returns:
            Logits tensor of shape (batch_size, num_items)
        """
        batch_size, seq_len = item_seq.shape

        # Create padding mask (True for padding positions)
        padding_mask = item_seq == 0

        # Get item embeddings
        item_emb = self.item_embedding(item_seq)  # (batch_size, seq_len, embedding_dim)

        # Get positional embeddings
        positions = (
            torch.arange(seq_len, device=item_seq.device)
            .unsqueeze(0)
            .expand(batch_size, -1)
        )
        pos_emb = self.positional_embedding(positions)

        # Combine embeddings
        x = item_emb + pos_emb
        x = self.layer_norm(x)
        x = self.dropout(x)

        # Create causal mask (prevent attending to future positions)
        causal_mask = self._generate_causal_mask(seq_len, item_seq.device)

        # Pass through transformer with both padding and causal masks
        x = self.transformer_encoder(
            x, mask=causal_mask, src_key_padding_mask=padding_mask
        )

        # Use the last non-padding position for each sequence
        # Get the last non-zero position for each sequence
        seq_lengths = (item_seq != 0).sum(dim=1) - 1
        seq_lengths = seq_lengths.clamp(min=0)

        # Gather the output at the last valid position
        last_items = x[torch.arange(batch_size), seq_lengths]

        # Project to item space
        logits = self.output_layer(last_items)

        return logits

    def predict_next_items(
        self, item_seq: torch.Tensor, top_k: int = 5
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Predict top-K next items.

        Args:
            item_seq: Tensor of shape (batch_size, seq_len) containing item indices
            top_k: Number of top items to return

        Returns:
            Tuple of (top_items, top_scores) tensors
            - top_items: Tensor of shape (batch_size, top_k) with item indices
            - top_scores: Tensor of shape (batch_size, top_k) with scores
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(item_seq)
            scores = torch.softmax(logits, dim=-1)

            # Get top-k items and scores
            top_scores, top_items = torch.topk(scores, k=top_k, dim=-1)

        return top_items, top_scores

    def _generate_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """
        Generate causal mask to prevent attending to future positions.

        Args:
            seq_len: Sequence length
            device: Device to create mask on

        Returns:
            Causal mask tensor of shape (seq_len, seq_len)
        """
        mask = torch.triu(torch.ones(seq_len, seq_len, device=device), diagonal=1)
        mask = mask.bool()
        mask = mask.masked_fill(mask == 1, float("-inf"))
        mask = mask.masked_fill(mask == 0, float(0.0))
        return mask
