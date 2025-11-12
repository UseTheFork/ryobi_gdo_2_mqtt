"""Tests for device manager."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ryobi_gdo_2_mqtt.device_manager import DeviceManager, RyobiDevice
from tests.conftest import load_fixture


@pytest.fixture
def mock_mqtt_settings():
    """Create mock MQTT settings."""
    from ha_mqtt_discoverable import Settings as MQTTSettings

    return MQTTSettings.MQTT(host="localhost", port=1883)


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = MagicMock()
    client.get_module = MagicMock(return_value=7)
    client.get_module_type = MagicMock(return_value=5)
    return client


@pytest.fixture
def mock_websocket():
    """Create mock WebSocket."""
    ws = MagicMock()
    ws.send_message = AsyncMock()
    return ws


@pytest.fixture
def device_manager(mock_mqtt_settings, mock_api_client):
    """Create a device manager instance."""
    return DeviceManager(mqtt_settings=mock_mqtt_settings, api_client=mock_api_client)


class TestRyobiDevice:
    """Tests for RyobiDevice."""

    @patch("ryobi_gdo_2_mqtt.device_manager.Cover")
    @patch("ryobi_gdo_2_mqtt.device_manager.Switch")
    @patch("ryobi_gdo_2_mqtt.device_manager.BinarySensor")
    def test_device_initialization(
        self, mock_binary_sensor, mock_switch, mock_cover, mock_mqtt_settings, mock_websocket, mock_api_client
    ):
        """Test device initialization creates all entities."""
        device = RyobiDevice(
            device_id="test_device",
            device_name="Test Device",
            mqtt_settings=mock_mqtt_settings,
            websocket=mock_websocket,
            api_client=mock_api_client,
        )

        assert device.device_id == "test_device"
        assert device.device_name == "Test Device"
        assert mock_cover.called
        assert mock_switch.called
        assert mock_binary_sensor.called

    @patch("ryobi_gdo_2_mqtt.device_manager.Cover")
    @patch("ryobi_gdo_2_mqtt.device_manager.Switch")
    @patch("ryobi_gdo_2_mqtt.device_manager.BinarySensor")
    def test_update_door_state(
        self, mock_binary_sensor, mock_switch, mock_cover, mock_mqtt_settings, mock_websocket, mock_api_client
    ):
        """Test updating door state."""
        mock_cover_instance = MagicMock()
        mock_cover.return_value = mock_cover_instance

        device = RyobiDevice(
            device_id="test_device",
            device_name="Test Device",
            mqtt_settings=mock_mqtt_settings,
            websocket=mock_websocket,
            api_client=mock_api_client,
        )

        # Reset mock after initialization
        mock_cover_instance.reset_mock()

        device.update_door_state("open")
        mock_cover_instance.open.assert_called_once()

        device.update_door_state("closed")
        mock_cover_instance.closed.assert_called_once()

    @patch("ryobi_gdo_2_mqtt.device_manager.Cover")
    @patch("ryobi_gdo_2_mqtt.device_manager.Switch")
    @patch("ryobi_gdo_2_mqtt.device_manager.BinarySensor")
    def test_update_light_state(
        self, mock_binary_sensor, mock_switch, mock_cover, mock_mqtt_settings, mock_websocket, mock_api_client
    ):
        """Test updating light state."""
        mock_switch_instance = MagicMock()
        mock_switch.return_value = mock_switch_instance

        device = RyobiDevice(
            device_id="test_device",
            device_name="Test Device",
            mqtt_settings=mock_mqtt_settings,
            websocket=mock_websocket,
            api_client=mock_api_client,
        )

        # Reset mock after initialization
        mock_switch_instance.reset_mock()

        device.update_light_state(True)
        mock_switch_instance.on.assert_called_once()

        device.update_light_state(False)
        mock_switch_instance.off.assert_called_once()

    @patch("ryobi_gdo_2_mqtt.device_manager.Cover")
    @patch("ryobi_gdo_2_mqtt.device_manager.Switch")
    @patch("ryobi_gdo_2_mqtt.device_manager.BinarySensor")
    def test_update_battery_level(
        self, mock_binary_sensor, mock_switch, mock_cover, mock_mqtt_settings, mock_websocket, mock_api_client
    ):
        """Test updating battery level."""
        mock_battery_instance = MagicMock()
        mock_binary_sensor.return_value = mock_battery_instance

        device = RyobiDevice(
            device_id="test_device",
            device_name="Test Device",
            mqtt_settings=mock_mqtt_settings,
            websocket=mock_websocket,
            api_client=mock_api_client,
        )

        # Low battery
        device.update_battery_level(15)
        mock_battery_instance.on.assert_called_once()

        # Normal battery
        device.update_battery_level(75)
        mock_battery_instance.off.assert_called_once()


class TestDeviceManager:
    """Tests for DeviceManager."""

    @pytest.mark.asyncio
    async def test_setup_device_success(self, device_manager, mock_websocket, fixtures_dir):
        """Test successful device setup."""
        device_manager.api_client.update_device = AsyncMock(
            return_value=MagicMock(door_state="closed", light_state=False, battery_level=0)
        )

        with patch("ryobi_gdo_2_mqtt.device_manager.RyobiDevice") as mock_device_class:
            mock_device = MagicMock()
            mock_device_class.return_value = mock_device

            device = await device_manager.setup_device("c4be84986d2e", "Acura", mock_websocket)

            assert device is not None
            assert "c4be84986d2e" in device_manager.devices

    @pytest.mark.asyncio
    async def test_setup_device_failure(self, device_manager, mock_websocket):
        """Test device setup failure."""
        device_manager.api_client.update_device = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Failed to get initial state"):
            await device_manager.setup_device("bad_device", "Bad Device", mock_websocket)

    @pytest.mark.asyncio
    async def test_handle_device_update(self, device_manager, fixtures_dir):
        """Test handling device updates from WebSocket."""
        # Setup a device first
        mock_device = MagicMock()
        mock_device.update_door_state = MagicMock()
        mock_device.update_light_state = MagicMock()
        device_manager.devices["c4be84986d2e"] = mock_device

        # Setup parser
        mock_parser = MagicMock()
        mock_parser.parse_attribute_update = MagicMock(return_value={"door_state": "open", "light_state": True})
        device_manager.parser = mock_parser

        # Handle update
        ws_data = load_fixture(fixtures_dir, "ws_message_1762952771.json")
        await device_manager.handle_device_update("c4be84986d2e", ws_data)

        mock_device.update_door_state.assert_called_once_with("open")
        mock_device.update_light_state.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_handle_device_update_unknown_device(self, device_manager, fixtures_dir):
        """Test handling update for unknown device."""
        ws_data = load_fixture(fixtures_dir, "ws_message_1762952771.json")

        # Should not raise, just log warning
        await device_manager.handle_device_update("unknown_device", ws_data)
