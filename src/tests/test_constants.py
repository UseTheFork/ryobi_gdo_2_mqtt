"""Tests for constants."""

from ryobi_gdo_2_mqtt.constants import DoorStates


class TestDoorStates:
    """Tests for DoorStates."""

    def test_door_states_to_string(self):
        """Test converting door state values to strings."""
        assert DoorStates.to_string(0) == "closed"
        assert DoorStates.to_string(1) == "open"
        assert DoorStates.to_string(2) == "closing"
        assert DoorStates.to_string(3) == "opening"
        assert DoorStates.to_string(4) == "fault"

    def test_door_states_unknown_value(self):
        """Test converting unknown door state value."""
        assert DoorStates.to_string(99) == "unknown"
        assert DoorStates.to_string(-1) == "unknown"
