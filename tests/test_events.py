"""Tests for event dispatcher, subscriptions, and pipeline patterns."""

import unittest
from src.events.dispatcher import EventDispatcher
from src.events.domain_events import BaseDomainEvent


class TestEvents(unittest.TestCase):
    def test_priority_subscription_order(self):
        dispatcher = EventDispatcher()
        execution_order = []

        dispatcher.subscribe("test.event", lambda ev: execution_order.append("low"), priority=10)
        dispatcher.subscribe("test.event", lambda ev: execution_order.append("high"), priority=100)
        dispatcher.subscribe("test.event", lambda ev: execution_order.append("mid"), priority=50)

        dispatcher.dispatch(BaseDomainEvent("test.event"))
        self.assertEqual(execution_order, ["high", "mid", "low"])

    def test_wildcard_listener(self):
        dispatcher = EventDispatcher()
        received = []

        dispatcher.subscribe("*", lambda ev: received.append(ev.name))
        dispatcher.dispatch(BaseDomainEvent("custom.event.one"))
        dispatcher.dispatch(BaseDomainEvent("custom.event.two"))

        self.assertEqual(received, ["custom.event.one", "custom.event.two"])

    def test_pipeline_pattern(self):
        dispatcher = EventDispatcher()

        dispatcher.subscribe("transform.text", lambda text: text.strip())
        dispatcher.subscribe("transform.text", lambda text: text.upper())

        result = dispatcher.pipeline("transform.text", "  hello world  ")
        self.assertEqual(result, "HELLO WORLD")


if __name__ == "__main__":
    unittest.main()
