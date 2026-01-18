"""Tests for SASRec model."""
import pytest
import torch
from src.models import SASRec


def test_sasrec_initialization():
    """Test SASRec model initialization."""
    model = SASRec(
        num_items=100,
        embedding_dim=128,
        num_heads=4,
        num_layers=2,
        dropout=0.1,
        max_seq_len=5
    )
    
    assert model.num_items == 100
    assert model.embedding_dim == 128
    assert model.max_seq_len == 5


def test_sasrec_forward():
    """Test SASRec forward pass."""
    model = SASRec(
        num_items=100,
        embedding_dim=128,
        num_heads=4,
        num_layers=2,
        dropout=0.1,
        max_seq_len=5
    )
    model.eval()
    
    # Create sample input
    batch_size = 2
    seq_len = 5
    item_seq = torch.randint(1, 101, (batch_size, seq_len))
    
    # Forward pass
    logits = model.forward(item_seq)
    
    assert logits.shape == (batch_size, 100)


def test_sasrec_predict_next_items():
    """Test prediction of next items."""
    model = SASRec(
        num_items=100,
        embedding_dim=128,
        num_heads=4,
        num_layers=2,
        dropout=0.1,
        max_seq_len=5
    )
    model.eval()
    
    # Create sample input
    batch_size = 2
    seq_len = 5
    top_k = 5
    item_seq = torch.randint(1, 101, (batch_size, seq_len))
    
    # Predict
    top_items, top_scores = model.predict_next_items(item_seq, top_k=top_k)
    
    assert top_items.shape == (batch_size, top_k)
    assert top_scores.shape == (batch_size, top_k)
    assert torch.all(top_scores[:, 0] >= top_scores[:, 1])  # Scores should be sorted
