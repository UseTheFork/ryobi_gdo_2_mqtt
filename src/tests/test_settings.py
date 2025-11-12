"""Tests for settings."""

import os
from unittest.mock import patch

from ryobi_gdo_2_mqtt.settings import Settings


class TestSettings:
    """Tests for Settings."""

    def test_settings_with_all_fields(self):
        """Test creating settings with all fields."""
        # Disable CLI parsing during tests
        with patch.dict(os.environ, {}, clear=False):
            settings = Settings(
                email="test@example.com",
                password="testpass",
                mqtt_host="localhost",
                mqtt_port=1883,
                mqtt_user="mqttuser",
                mqtt_password="mqttpass",
                log_level="DEBUG",
                _cli_parse_args=False,
            )

        assert settings.email == "test@example.com"
        assert settings.password.get_secret_value() == "testpass"
        assert settings.mqtt_host == "localhost"
        assert settings.mqtt_port == 1883
        assert settings.mqtt_user == "mqttuser"
        assert settings.mqtt_password.get_secret_value() == "mqttpass"

    def test_settings_with_defaults(self):
        """Test creating settings with default values."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.argv", ["test"]):
                settings = Settings(email="test@example.com", password="testpass", mqtt_host="localhost")

        assert settings.mqtt_port == 1883
        assert settings.mqtt_user == ""
        assert settings.mqtt_password.get_secret_value() == ""

    def test_settings_password_is_secret(self):
        """Test that password is stored as SecretStr."""
        with patch.dict(os.environ, {}, clear=False):
            settings = Settings(
                email="test@example.com", password="testpass", mqtt_host="localhost", _cli_parse_args=False
            )

        # Password should not be visible in repr
        assert "testpass" not in str(settings)
        assert "testpass" not in repr(settings)

        # But can be accessed via get_secret_value()
        assert settings.password.get_secret_value() == "testpass"
