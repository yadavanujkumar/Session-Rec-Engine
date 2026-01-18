# Quick Start Guide

This guide will help you get the Session-Based Recommendation System up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (recommended)
- 4GB RAM minimum

## Quick Start with Docker Compose (Easiest)

### Step 1: Clone and Start Services

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/Session-Rec-Engine.git
cd Session-Rec-Engine

# Start all services (API, Redis, Qdrant)
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### Step 2: Verify Services are Running

```bash
# Check health
curl http://localhost:8000/api/v1/health

# Should return:
# {
#   "status": "healthy",
#   "components": {
#     "session_store": true,
#     "vector_store": true,
#     "model": true
#   }
# }
```

### Step 3: Try the API

Open your browser and go to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Step 4: Simulate a User Session

```bash
# Run the example script
docker-compose exec api python example_usage.py
```

## Quick Start without Docker

### Step 1: Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/Session-Rec-Engine.git
cd Session-Rec-Engine

# Run setup script
./setup.sh
# OR manually:
# python -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt
```

### Step 2: Start Required Services

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### Step 3: Start the API

```bash
# Terminal 3: Start the API (with virtual environment activated)
python main.py
```

### Step 4: Test the API

```bash
# In another terminal, run the example
python example_usage.py
```

## Using the API

### 1. Record a Click Event

```bash
curl -X POST http://localhost:8000/api/v1/click \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_123",
    "item_id": "item_0010"
  }'
```

### 2. Get Recommendations

```bash
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user_123"
  }'
```

**Response:**
```json
{
  "session_id": "user_123",
  "recommendations": ["item_0042", "item_0015", "item_0088", "item_0003", "item_0091"],
  "used_coldstart": false,
  "message": "Recommendations generated using model-based strategy"
}
```

### 3. View Metrics

```bash
curl http://localhost:8000/api/v1/metrics
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

## Understanding the System

### Cold-Start Behavior

- **First click**: System uses Multi-Armed Bandit to serve trending items
- **After 2+ clicks**: System uses the SASRec model for personalized recommendations
- **Privacy**: Sessions automatically expire after 30 minutes

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/click` | POST | Record a click event |
| `/api/v1/recommend` | POST | Get recommendations |
| `/api/v1/feedback` | POST | Record feedback for learning |
| `/api/v1/metrics` | GET | View system metrics |
| `/api/v1/health` | GET | Check system health |
| `/docs` | GET | Interactive API documentation |

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Run Tests**: `pytest tests/ -v`
3. **Train a Model**: `python train.py --num-epochs 20`
4. **Customize**: Edit `.env` file to adjust configuration
5. **Read the Docs**: Check `README.md` for detailed information

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml or .env
# For example, change API_PORT from 8000 to 8080
```

### Redis Connection Error

```bash
# Make sure Redis is running
redis-cli ping
# Should return: PONG
```

### Qdrant Connection Error

```bash
# Check if Qdrant is running
curl http://localhost:6333/healthz
# Should return: {"status":"ok"}
```

### Import Errors

```bash
# Make sure you're in the project root and virtual environment is activated
cd /path/to/Session-Rec-Engine
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Stopping the System

### Docker Compose

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Manual Setup

```bash
# Stop the API: Press Ctrl+C in the terminal running main.py
# Stop Redis: Press Ctrl+C in the terminal running redis-server
# Stop Qdrant: docker stop <container_id>
```

## Support

- **Issues**: https://github.com/yadavanujkumar/Session-Rec-Engine/issues
- **Documentation**: See `README.md`
- **Examples**: See `example_usage.py`
