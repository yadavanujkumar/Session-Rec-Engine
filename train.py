"""Training script for SASRec model."""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import List, Tuple
import argparse

from src.models import SASRec
from src.utils import ItemCatalog
from src.config import get_settings


class SessionDataset(Dataset):
    """Dataset for session-based training."""
    
    def __init__(self, sequences: List[List[int]], sequence_length: int = 5):
        """
        Initialize dataset.
        
        Args:
            sequences: List of item ID sequences
            sequence_length: Maximum sequence length
        """
        self.sequences = sequences
        self.sequence_length = sequence_length
        self.samples = self._create_samples()
    
    def _create_samples(self) -> List[Tuple[List[int], int]]:
        """Create training samples from sequences."""
        samples = []
        
        for seq in self.sequences:
            # Need at least 2 items (input and target)
            if len(seq) < 2:
                continue
            
            # Create multiple samples from each sequence
            for i in range(1, len(seq)):
                input_seq = seq[:i]
                target = seq[i]
                
                # Pad or truncate input sequence
                if len(input_seq) < self.sequence_length:
                    input_seq = [0] * (self.sequence_length - len(input_seq)) + input_seq
                else:
                    input_seq = input_seq[-self.sequence_length:]
                
                samples.append((input_seq, target))
        
        return samples
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        input_seq, target = self.samples[idx]
        return torch.tensor(input_seq, dtype=torch.long), torch.tensor(target, dtype=torch.long)


def generate_synthetic_data(
    num_items: int = 100,
    num_sequences: int = 1000,
    min_seq_len: int = 3,
    max_seq_len: int = 10
) -> List[List[int]]:
    """
    Generate synthetic session data for training.
    
    Args:
        num_items: Number of items in catalog
        num_sequences: Number of sequences to generate
        min_seq_len: Minimum sequence length
        max_seq_len: Maximum sequence length
        
    Returns:
        List of item ID sequences
    """
    sequences = []
    
    for _ in range(num_sequences):
        seq_len = np.random.randint(min_seq_len, max_seq_len + 1)
        # Generate sequences with some temporal correlation
        start_item = np.random.randint(1, num_items + 1)
        sequence = [start_item]
        
        for _ in range(seq_len - 1):
            # 70% chance to pick nearby item, 30% random
            if np.random.random() < 0.7:
                next_item = start_item + np.random.randint(-5, 6)
                next_item = max(1, min(num_items, next_item))
            else:
                next_item = np.random.randint(1, num_items + 1)
            sequence.append(next_item)
            start_item = next_item
        
        sequences.append(sequence)
    
    return sequences


def train_model(
    model: SASRec,
    train_loader: DataLoader,
    num_epochs: int = 10,
    learning_rate: float = 0.001,
    device: str = "cpu"
):
    """
    Train the SASRec model.
    
    Args:
        model: SASRec model
        train_loader: Training data loader
        num_epochs: Number of training epochs
        learning_rate: Learning rate
        device: Device to train on
    """
    model.to(device)
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    print(f"Training on {device}")
    print(f"Total samples: {len(train_loader.dataset)}")
    print(f"Batch size: {train_loader.batch_size}")
    print(f"Number of epochs: {num_epochs}\n")
    
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        num_batches = 0
        
        for batch_idx, (sequences, targets) in enumerate(train_loader):
            sequences = sequences.to(device)
            targets = targets.to(device)
            
            # Forward pass
            optimizer.zero_grad()
            logits = model(sequences)
            loss = criterion(logits, targets)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            if (batch_idx + 1) % 50 == 0:
                avg_loss = total_loss / num_batches
                print(f"Epoch [{epoch+1}/{num_epochs}], "
                      f"Batch [{batch_idx+1}/{len(train_loader)}], "
                      f"Loss: {avg_loss:.4f}")
        
        avg_epoch_loss = total_loss / num_batches
        print(f"Epoch [{epoch+1}/{num_epochs}] completed. Average Loss: {avg_epoch_loss:.4f}\n")
    
    print("Training completed!")


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train SASRec model")
    parser.add_argument("--num-items", type=int, default=100, help="Number of items")
    parser.add_argument("--num-sequences", type=int, default=1000, help="Number of training sequences")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--num-epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--output", type=str, default="model.pth", help="Output model path")
    args = parser.parse_args()
    
    # Get settings
    settings = get_settings()
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}\n")
    
    # Generate synthetic data
    print("Generating synthetic training data...")
    sequences = generate_synthetic_data(
        num_items=args.num_items,
        num_sequences=args.num_sequences
    )
    print(f"Generated {len(sequences)} sequences\n")
    
    # Create dataset and dataloader
    dataset = SessionDataset(sequences, sequence_length=settings.sequence_length)
    train_loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0
    )
    
    # Create model
    print("Creating model...")
    model = SASRec(
        num_items=args.num_items,
        embedding_dim=settings.embedding_dim,
        num_heads=settings.num_heads,
        num_layers=settings.num_layers,
        dropout=settings.dropout,
        max_seq_len=settings.sequence_length
    )
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters\n")
    
    # Train model
    train_model(
        model,
        train_loader,
        num_epochs=args.num_epochs,
        learning_rate=args.learning_rate,
        device=device
    )
    
    # Save model
    print(f"Saving model to {args.output}...")
    torch.save({
        'model_state_dict': model.state_dict(),
        'num_items': args.num_items,
        'config': {
            'embedding_dim': settings.embedding_dim,
            'num_heads': settings.num_heads,
            'num_layers': settings.num_layers,
            'dropout': settings.dropout,
            'sequence_length': settings.sequence_length
        }
    }, args.output)
    print("✓ Model saved successfully!")


if __name__ == "__main__":
    main()
