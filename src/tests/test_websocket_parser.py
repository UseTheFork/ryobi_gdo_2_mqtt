"""Tests for WebSocket message parser."""

import pytest

from ryobi_gdo_2_mqtt.websocket_parser import WebSocketMessageParser
from tests.conftest import load_fixture


@pytest.fixture
def parser():
    """Create a parser instance."""
    return WebSocketMessageParser()


class TestWebSocketMessageParser:
    """Tests for WebSocketMessageParser."""

    def test_parse_light_state_on(self, parser, fixtures_dir):
        """Test parsing light state change to ON."""
        data = load_fixture(fixtures_dir, "ws_message_1762952732.json")

        updates = parser.parse_attribute_update(data)

        assert "light_state" in updates
        assert updates["light_state"] is True

    def test_parse_light_state_off(self, parser, fixtures_dir):
        """Test parsing light state change to OFF."""
        data = load_fixture(fixtures_dir, "ws_message_1762952736.json")

        updates = parser.parse_attribute_update(data)

        assert "light_state" in updates
        assert updates["light_state"] is False

    def test_parse_door_state_open(self, parser, fixtures_dir):
        """Test parsing door state change to OPEN."""
        data = load_fixture(fixtures_dir, "ws_message_1762952771.json")

        updates = parser.parse_attribute_update(data)

        assert "door_state" in updates
        assert updates["door_state"] == "open"

    def test_parse_door_state_closed(self, parser, fixtures_dir):
        """Test parsing door state change to CLOSED."""
        data = load_fixture(fixtures_dir, "ws_message_1762952798.json")

        updates = parser.parse_attribute_update(data)

        assert "door_state" in updates
        assert updates["door_state"] == "closed"

    def test_parse_door_position_only(self, parser, fixtures_dir):
        """Test parsing door position update without state change."""
        data = load_fixture(fixtures_dir, "ws_message_1762952767.json")

        updates = parser.parse_attribute_update(data)

        # Should not include door_state, only position updates
        assert "door_state" not in updates

    def test_parse_non_attribute_update_message(self, parser, fixtures_dir):
        """Test that non-attribute-update messages return empty dict."""
        data = load_fixture(fixtures_dir, "ws_message_1762952686.json")

        updates = parser.parse_attribute_update(data)

        assert updates == {}

    def test_parse_multiple_attributes(self, parser, fixtures_dir):
        """Test parsing message with multiple attribute updates."""
        data = load_fixture(fixtures_dir, "ws_message_1762952771.json")

        updates = parser.parse_attribute_update(data)

        # This message has both doorState and doorPosition
        assert "door_state" in updates
        assert updates["door_state"] == "open"
