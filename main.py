"""Main entry point for the recommendation service."""
import uvicorn
from src.config import get_settings


def main():
    """Run the FastAPI application."""
    settings = get_settings()
    
    uvicorn.run(
        "src.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
