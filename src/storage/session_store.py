"""Redis session store for managing user sessions."""
import redis
import json
from typing import List, Optional
from datetime import datetime


class SessionStore:
    """Redis-based session store with automatic expiry."""
    
    def __init__(self, host: str, port: int, db: int, expiry_seconds: int):
        """
        Initialize session store.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            expiry_seconds: Session expiry time in seconds
        """
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.expiry_seconds = expiry_seconds
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session."""
        return f"session:{session_id}"
    
    def add_click(self, session_id: str, item_id: str) -> None:
        """
        Add a click event to a session.
        
        Args:
            session_id: Unique session identifier
            item_id: Item that was clicked
        """
        key = self._get_session_key(session_id)
        
        # Get current session data
        session_data = self.get_session(session_id) or []
        
        # Add new click with timestamp
        click_data = {
            "item_id": item_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        session_data.append(click_data)
        
        # Store back to Redis with expiry
        self.redis_client.setex(
            key,
            self.expiry_seconds,
            json.dumps(session_data)
        )
    
    def get_session(self, session_id: str) -> Optional[List[dict]]:
        """
        Get session data.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of click events or None if session doesn't exist
        """
        key = self._get_session_key(session_id)
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    def get_item_sequence(self, session_id: str, max_length: int = 5) -> List[str]:
        """
        Get the sequence of item IDs from a session.
        
        Args:
            session_id: Unique session identifier
            max_length: Maximum sequence length
            
        Returns:
            List of item IDs (most recent items)
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return []
        
        # Extract item IDs and return last max_length items
        item_ids = [click["item_id"] for click in session_data]
        return item_ids[-max_length:]
    
    def get_session_length(self, session_id: str) -> int:
        """
        Get the number of clicks in a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Number of clicks in the session
        """
        session_data = self.get_session(session_id)
        return len(session_data) if session_data else 0
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete a session.
        
        Args:
            session_id: Unique session identifier
        """
        key = self._get_session_key(session_id)
        self.redis_client.delete(key)
    
    def health_check(self) -> bool:
        """Check if Redis is healthy."""
        try:
            return self.redis_client.ping()
        except Exception:
            return False
