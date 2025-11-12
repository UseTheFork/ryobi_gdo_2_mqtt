"""Tests for custom exceptions."""

import pytest

from ryobi_gdo_2_mqtt.exceptions import (
    RyobiApiError,
    RyobiAuthenticationError,
    RyobiConnectionError,
    RyobiDeviceNotFoundError,
    RyobiInvalidResponseError,
)


class TestExceptions:
    """Tests for custom exceptions."""

    def test_base_exception(self):
        """Test base RyobiApiError exception."""
        with pytest.raises(RyobiApiError, match="Base error"):
            raise RyobiApiError("Base error")

    def test_authentication_error_inherits_from_base(self):
        """Test RyobiAuthenticationError inherits from RyobiApiError."""
        assert issubclass(RyobiAuthenticationError, RyobiApiError)

        with pytest.raises(RyobiApiError):
            raise RyobiAuthenticationError("Auth failed")

    def test_connection_error_inherits_from_base(self):
        """Test RyobiConnectionError inherits from RyobiApiError."""
        assert issubclass(RyobiConnectionError, RyobiApiError)

        with pytest.raises(RyobiApiError):
            raise RyobiConnectionError("Connection failed")

    def test_device_not_found_error_inherits_from_base(self):
        """Test RyobiDeviceNotFoundError inherits from RyobiApiError."""
        assert issubclass(RyobiDeviceNotFoundError, RyobiApiError)

        with pytest.raises(RyobiApiError):
            raise RyobiDeviceNotFoundError("Device not found")

    def test_invalid_response_error_inherits_from_base(self):
        """Test RyobiInvalidResponseError inherits from RyobiApiError."""
        assert issubclass(RyobiInvalidResponseError, RyobiApiError)

        with pytest.raises(RyobiApiError):
            raise RyobiInvalidResponseError("Invalid response")

    def test_exception_messages(self):
        """Test that exception messages are preserved."""
        error_msg = "Custom error message"

        with pytest.raises(RyobiAuthenticationError, match=error_msg):
            raise RyobiAuthenticationError(error_msg)
