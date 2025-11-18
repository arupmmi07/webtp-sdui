"""Abstract event bus interface for agent-to-agent communication."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List
from datetime import datetime
import uuid


@dataclass
class Event:
    """Standard event format for A2A communication."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    appointment_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source_agent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "appointment_id": self.appointment_id,
            "session_id": self.session_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source_agent": self.source_agent,
        }


class EventBus(ABC):
    """
    Abstract base class for event bus implementations.
    
    Implementations: MemoryQueueAdapter (start), RedisAdapter (scale)
    Enables agent-to-agent communication without tight coupling.
    """
    
    @abstractmethod
    def emit(self, event: Event):
        """
        Emit an event to the bus.
        
        Args:
            event: Event to emit
        """
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[Event], None]):
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of event to listen for
            handler: Callback function to handle the event
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]):
        """
        Unsubscribe from events.
        
        Args:
            event_type: Type of event to stop listening for
            handler: Handler to remove
        """
        pass
    
    @abstractmethod
    def get_events(self, event_type: Optional[str] = None, session_id: Optional[str] = None) -> List[Event]:
        """
        Get events from the bus.
        
        Args:
            event_type: Filter by event type (optional)
            session_id: Filter by session ID (optional)
        
        Returns:
            List of events matching the filters
        """
        pass
    
    @abstractmethod
    def clear(self):
        """Clear all events from the bus."""
        pass

