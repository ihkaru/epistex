"""Contracts for Event-Driven Architecture."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
import time


class EventInterface(ABC):
    """Abstract contract for all domain events."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical name of the event."""
        raise NotImplementedError

    @property
    @abstractmethod
    def timestamp(self) -> float:
        """Epoch timestamp when the event was fired."""
        raise NotImplementedError

    @property
    @abstractmethod
    def payload(self) -> Dict[str, Any]:
        """Event payload data dictionary."""
        raise NotImplementedError


class EventDispatcherInterface(ABC):
    """Abstract contract for event dispatching and subscription."""

    @abstractmethod
    def subscribe(self, event_name: str, handler: Callable[..., Any], priority: int = 0) -> None:
        """Subscribe a listener callable to an event with optional priority."""
        raise NotImplementedError

    @abstractmethod
    def dispatch(self, event: EventInterface) -> None:
        """Dispatch a domain event to all subscribed listeners."""
        raise NotImplementedError

    @abstractmethod
    def pipeline(self, event_name: str, data: Any = None) -> Any:
        """Pass data through listeners sequentially in a pipeline pattern."""
        raise NotImplementedError
