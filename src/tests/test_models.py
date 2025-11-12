"""Tests for data models."""

from ryobi_gdo_2_mqtt.models import DeviceData, LoginResponse
from tests.conftest import load_fixture


class TestLoginResponse:
    """Tests for LoginResponse model."""

    def test_login_response_parsing(self, fixtures_dir):
        """Test parsing login response from fixture."""
        data = load_fixture(fixtures_dir, "login_response.json")

        response = LoginResponse(**data)

        assert response.api_key == "1234567890"
        assert response.result.varName == "user@email.mail"
        assert response.result.auth.apiKey == "1234567890"


class TestDeviceData:
    """Tests for DeviceData model."""

    def test_device_data_all_fields(self):
        """Test creating DeviceData with all fields."""
        data = DeviceData(
            door_state="open", light_state=True, battery_level=75, safety=0, vacation_mode=0, device_name="Test Device"
        )

        assert data.door_state == "open"
        assert data.light_state is True
        assert data.battery_level == 75
        assert data.device_name == "Test Device"

    def test_device_data_optional_fields(self):
        """Test creating DeviceData with only required fields."""
        data = DeviceData()

        assert data.door_state is None
        assert data.light_state is None
        assert data.battery_level is None
        assert data.device_name is None
