"""Central event dispatcher supporting publish/subscribe and pipeline patterns."""

from typing import Any, Callable, Dict, List, Tuple
from src.contracts.events import EventDispatcherInterface, EventInterface


class EventDispatcher(EventDispatcherInterface):
    """Event dispatcher for decoupled event-driven architecture."""

    def __init__(self) -> None:
        # Map: event_name -> List of (priority, handler_callable)
        self._listeners: Dict[str, List[Tuple[int, Callable[..., Any]]]] = {}

    def subscribe(self, event_name: str, handler: Callable[..., Any], priority: int = 0) -> None:
        """Register a listener for an event. Higher priority handlers run first."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append((priority, handler))
        # Sort descending by priority
        self._listeners[event_name].sort(key=lambda item: item[0], reverse=True)

    def dispatch(self, event: EventInterface) -> None:
        """Dispatch a domain event to all subscribed listeners and global listeners."""
        # Specific event listeners
        if event.name in self._listeners:
            for _, handler in self._listeners[event.name]:
                try:
                    handler(event)
                except Exception:
                    pass

        # Wildcard listeners
        if "*" in self._listeners:
            for _, handler in self._listeners["*"]:
                try:
                    handler(event)
                except Exception:
                    pass

    def pipeline(self, event_name: str, data: Any = None) -> Any:
        """Pass payload through listener pipeline sequentially."""
        if event_name in self._listeners:
            for _, handler in self._listeners[event_name]:
                try:
                    res = handler(data)
                    if res is not None:
                        data = res
                except Exception:
                    pass
        return data


_GLOBAL_DISPATCHER: EventDispatcher | None = None


def get_event_dispatcher() -> EventDispatcher:
    """Retrieve global application event dispatcher singleton."""
    global _GLOBAL_DISPATCHER
    if _GLOBAL_DISPATCHER is None:
        _GLOBAL_DISPATCHER = EventDispatcher()
    return _GLOBAL_DISPATCHER
