# Session-Rec-Engine

## Privacy-First Session-Based Recommendation System

A real-time, privacy-preserving recommendation system that personalizes content for anonymous users without storing persistent user profiles. Sessions automatically expire after 30 minutes, ensuring user privacy.

## 🎯 Features

### Core Components

1. **Transformer-Based Model (SASRec)**
   - Self-Attentive Sequential Recommendation using PyTorch
   - Processes sequences of last 5 item interactions
   - Predicts next items based on session history
   - Real-time inference with low latency

2. **Real-Time Inference Pipeline**
   - **FastAPI** endpoints for click event ingestion
   - **Redis** as session store with 30-minute auto-expiry (privacy-first)
   - **Qdrant** vector database for top-K item retrieval
   - Sub-100ms latency for recommendations

3. **Cold-Start Handler**
   - Multi-Armed Bandit (Thompson Sampling) algorithm
   - Serves trending items when session length < 2 clicks
   - Balances exploration vs. exploitation
   - Continuously learns from user feedback

4. **Observability Dashboard**
   - Real-time Hit Rate@10 (recommendation accuracy)
   - P99 Latency tracking (99th percentile response time)
   - Request statistics and cold-start metrics
   - Health monitoring for all components

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────────────┐
│          FastAPI Application            │
│  ┌─────────────────────────────────┐   │
│  │   Recommendation Service        │   │
│  │  ┌──────────┐  ┌──────────┐    │   │
│  │  │ SASRec   │  │ Multi-   │    │   │
│  │  │ Model    │  │ Armed    │    │   │
│  │  │          │  │ Bandit   │    │   │
│  │  └──────────┘  └──────────┘    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
       │              │              │
       ▼              ▼              ▼
  ┌────────┐    ┌─────────┐   ┌─────────┐
  │ Redis  │    │ Qdrant  │   │ Metrics │
  │Session │    │ Vector  │   │Tracker  │
  │ Store  │    │   DB    │   │         │
  └────────┘    └─────────┘   └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (recommended)
- Redis and Qdrant (or use Docker Compose)

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/Session-Rec-Engine.git
cd Session-Rec-Engine

# Start all services (API, Redis, Qdrant)
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f api
```

The API will be available at `http://localhost:8000`

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/Session-Rec-Engine.git
cd Session-Rec-Engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Redis (in separate terminal)
redis-server

# Start Qdrant (in separate terminal)
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Copy environment file and adjust if needed
cp .env.example .env

# Run the application
python main.py
```

## 📖 API Documentation

### Interactive Documentation

Once the service is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### 1. Record Click Event
```http
POST /api/v1/click
Content-Type: application/json

{
  "session_id": "user_12345",
  "item_id": "item_0042"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Click event recorded for session user_12345"
}
```

#### 2. Get Recommendations
```http
POST /api/v1/recommend
Content-Type: application/json

{
  "session_id": "user_12345"
}
```

**Response:**
```json
{
  "session_id": "user_12345",
  "recommendations": ["item_0042", "item_0015", "item_0088", "item_0003", "item_0091"],
  "used_coldstart": false,
  "message": "Recommendations generated using model-based strategy"
}
```

#### 3. Record Feedback
```http
POST /api/v1/feedback
Content-Type: application/json

{
  "session_id": "user_12345",
  "recommended_items": ["item_0042", "item_0015", "item_0088"],
  "clicked_item": "item_0042"
}
```

#### 4. Get Metrics (Observability Dashboard)
```http
GET /api/v1/metrics
```

**Response:**
```json
{
  "hit_rate_at_10": 67.5,
  "p99_latency_ms": 45.2,
  "p50_latency_ms": 12.5,
  "avg_latency_ms": 15.8,
  "total_requests": 1250,
  "coldstart_requests": 425,
  "model_requests": 825,
  "coldstart_percentage": 34.0
}
```

#### 5. Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "session_store": true,
    "vector_store": true,
    "model": true
  }
}
```

## 💡 Example Usage

Run the example script to simulate user sessions:

```bash
# Make sure the API is running
python main.py

# In another terminal, run the example
python example_usage.py
```

### Python Client Example

```python
import requests

# Record a click
requests.post("http://localhost:8000/api/v1/click", json={
    "session_id": "session_001",
    "item_id": "item_0010"
})

# Get recommendations
response = requests.post("http://localhost:8000/api/v1/recommend", json={
    "session_id": "session_001"
})

recommendations = response.json()
print(recommendations)
```

### cURL Examples

```bash
# Record a click
curl -X POST http://localhost:8000/api/v1/click \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_001", "item_id": "item_0010"}'

# Get recommendations
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"session_id": "session_001"}'

# Get metrics
curl http://localhost:8000/api/v1/metrics
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🎓 Training the Model

The system includes a training script for the SASRec model. You can train on synthetic data or your own session data:

```bash
# Train with default settings (synthetic data)
python train.py

# Train with custom parameters
python train.py --num-items 200 --num-sequences 5000 --batch-size 64 --num-epochs 20

# Save to specific location
python train.py --output models/my_model.pth
```

**Training Parameters:**
- `--num-items`: Number of items in catalog (default: 100)
- `--num-sequences`: Number of training sequences (default: 1000)
- `--batch-size`: Training batch size (default: 32)
- `--num-epochs`: Number of training epochs (default: 10)
- `--learning-rate`: Learning rate (default: 0.001)
- `--output`: Path to save trained model (default: model.pth)

The training script generates synthetic session data with temporal correlation to simulate realistic user behavior patterns.

## 🔧 Configuration

Configuration is managed through environment variables or `.env` file:

```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
SESSION_EXPIRY_SECONDS=1800  # 30 minutes

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=items

# Model Configuration
MODEL_NAME=sasrec
SEQUENCE_LENGTH=5
EMBEDDING_DIM=128
NUM_HEADS=4
NUM_LAYERS=2
DROPOUT=0.1

# Recommendation Configuration
TOP_K=5
COLD_START_THRESHOLD=2

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 🔒 Privacy Features

1. **Automatic Session Expiry**: Sessions expire after 30 minutes of inactivity
2. **No Persistent User Profiles**: No data is stored beyond the session lifetime
3. **Anonymous Sessions**: Only session IDs are used, no PII required
4. **In-Memory Processing**: Minimal data persistence

## 📊 Performance Characteristics

- **Latency**: 
  - P50: ~10-15ms
  - P99: ~40-50ms
- **Throughput**: 100+ requests/second (single instance)
- **Memory**: ~500MB base + model size
- **Session Storage**: Redis with LRU eviction

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Deep Learning**: PyTorch
- **Session Store**: Redis
- **Vector Database**: Qdrant
- **ML Algorithm**: Thompson Sampling (Multi-Armed Bandit)
- **Model**: SASRec (Self-Attentive Sequential Recommendation)

## 📁 Project Structure

```
Session-Rec-Engine/
├── src/
│   ├── api/                 # FastAPI application
│   │   └── app.py
│   ├── models/              # SASRec model
│   │   └── sasrec.py
│   ├── storage/             # Redis & Qdrant
│   │   ├── session_store.py
│   │   └── vector_store.py
│   ├── coldstart/           # Multi-Armed Bandit
│   │   └── bandit.py
│   ├── monitoring/          # Metrics tracking
│   │   └── metrics.py
│   ├── utils/               # Utilities
│   │   └── catalog.py
│   ├── config.py            # Configuration
│   └── service.py           # Main service
├── tests/                   # Test suite
├── main.py                  # Entry point
├── example_usage.py         # Usage examples
├── requirements.txt         # Dependencies
├── docker-compose.yml       # Docker setup
├── Dockerfile
└── README.md
```

## 🚦 Development

### Code Style

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

### Adding New Items

Items are automatically created on startup with a sample catalog. To add custom items:

```python
from src.utils import ItemCatalog

catalog = ItemCatalog()
catalog.add_items([
    {"item_id": "item_custom_001", "name": "Custom Product", "category": "Custom"},
    {"item_id": "item_custom_002", "name": "Another Product", "category": "Custom"}
])
```

## 📈 Metrics & Monitoring

The system tracks:

- **Hit Rate@10**: Percentage of recommendations that were clicked (accuracy)
- **P99 Latency**: 99th percentile response time (speed)
- **P50 Latency**: Median response time
- **Request Counts**: Total, cold-start, and model-based requests
- **Cold-start Percentage**: How often cold-start logic is used

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SASRec paper: "Self-Attentive Sequential Recommendation" (Kang & McAuley, 2018)
- BERT4Rec: "BERT4Rec: Sequential Recommendation with Bidirectional Encoder Representations from Transformer" (Sun et al., 2019)
- Thompson Sampling for Multi-Armed Bandits

## 📧 Contact

For questions or support, please open an issue on GitHub.