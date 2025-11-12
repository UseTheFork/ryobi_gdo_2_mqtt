"""Tests for WebSocket client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession, WSMsgType

from ryobi_gdo_2_mqtt.websocket import (
    STATE_CONNECTED,
    STATE_DISCONNECTED,
    STATE_STOPPED,
    RyobiWebSocket,
)


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    return MagicMock(spec=ClientSession)


@pytest.fixture
def mock_callback():
    """Create a mock callback function."""
    return AsyncMock()


@pytest.fixture
def websocket_client(mock_session, mock_callback):
    """Create a WebSocket client instance."""
    return RyobiWebSocket(
        callback=mock_callback,
        username="test@example.com",
        apikey="test_api_key",
        device="test_device",
        session=mock_session,
    )


class TestRyobiWebSocket:
    """Tests for RyobiWebSocket."""

    def test_initialization(self, websocket_client):
        """Test WebSocket client initialization."""
        assert websocket_client._user == "test@example.com"
        assert websocket_client._apikey == "test_api_key"
        assert websocket_client._device_id == "test_device"
        assert websocket_client.failed_attempts == 0
        assert websocket_client._state is None

    @pytest.mark.asyncio
    async def test_set_state_calls_callback(self, websocket_client, mock_callback):
        """Test that setting state calls the callback."""
        await websocket_client.set_state(STATE_CONNECTED)

        assert websocket_client.state == STATE_CONNECTED
        mock_callback.assert_called_once_with("websocket_state", STATE_CONNECTED, None)

    @pytest.mark.asyncio
    async def test_websocket_auth_sends_correct_message(self, websocket_client):
        """Test that websocket_auth sends correct authentication message."""
        websocket_client.websocket_send = AsyncMock()

        await websocket_client.websocket_auth()

        websocket_client.websocket_send.assert_called_once()
        call_args = websocket_client.websocket_send.call_args[0][0]
        assert call_args["method"] == "srvWebSocketAuth"
        assert call_args["params"]["varName"] == "test@example.com"
        assert call_args["params"]["apiKey"] == "test_api_key"

    @pytest.mark.asyncio
    async def test_websocket_subscribe_sends_correct_message(self, websocket_client):
        """Test that websocket_subscribe sends correct subscription message."""
        websocket_client.websocket_send = AsyncMock()

        await websocket_client.websocket_subscribe()

        websocket_client.websocket_send.assert_called_once()
        call_args = websocket_client.websocket_send.call_args[0][0]
        assert call_args["method"] == "wskSubscribe"
        assert call_args["params"]["topic"] == "test_device.wskAttributeUpdateNtfy"

    @pytest.mark.asyncio
    async def test_websocket_send_success(self, websocket_client):
        """Test successful websocket message sending."""
        mock_ws_client = MagicMock()
        mock_ws_client.send_str = AsyncMock()
        websocket_client._ws_client = mock_ws_client

        message = {"test": "message"}
        result = await websocket_client.websocket_send(message)

        assert result is True
        mock_ws_client.send_str.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_send_failure(self, websocket_client, mock_callback):
        """Test websocket message sending failure."""
        mock_ws_client = MagicMock()
        mock_ws_client.send_str = AsyncMock(side_effect=Exception("Send failed"))
        websocket_client._ws_client = mock_ws_client

        message = {"test": "message"}
        result = await websocket_client.websocket_send(message)

        assert result is False
        assert websocket_client.state == STATE_DISCONNECTED

    def test_redact_api_key(self, websocket_client):
        """Test that API key is redacted from messages."""
        message = {"params": {"apiKey": "secret_key", "other": "data"}}

        redacted = websocket_client.redact_api_key(message)

        assert "secret_key" not in redacted
        assert '"apiKey": ""' in redacted

    @pytest.mark.asyncio
    async def test_send_message_when_connected(self, websocket_client):
        """Test sending command message when connected."""
        websocket_client._state = STATE_CONNECTED
        websocket_client.websocket_send = AsyncMock()

        await websocket_client.send_message(7, 5, "doorCommand", 1)

        websocket_client.websocket_send.assert_called_once()
        call_args = websocket_client.websocket_send.call_args[0][0]
        assert call_args["method"] == "gdoModuleCommand"
        assert call_args["params"]["portId"] == 7
        assert call_args["params"]["moduleType"] == 5
        assert call_args["params"]["moduleMsg"]["doorCommand"] == 1

    @pytest.mark.asyncio
    async def test_send_message_when_not_connected(self, websocket_client):
        """Test that send_message does nothing when not connected."""
        websocket_client._state = STATE_DISCONNECTED
        websocket_client.websocket_send = AsyncMock()

        await websocket_client.send_message(7, 5, "doorCommand", 1)

        websocket_client.websocket_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_sets_state_to_stopped(self, websocket_client, mock_callback):
        """Test that close sets state to stopped."""
        await websocket_client.close()

        assert websocket_client.state == STATE_STOPPED
        mock_callback.assert_called_once_with("websocket_state", STATE_STOPPED, None)

    @pytest.mark.asyncio
    async def test_running_handles_text_messages(self, websocket_client, mock_callback):
        """Test that running handles text messages correctly."""
        mock_ws_client = MagicMock()
        mock_message = MagicMock()
        mock_message.type = WSMsgType.TEXT
        mock_message.json.return_value = {"test": "data"}

        # Create async iterator that yields one message then stops
        async def mock_iter():
            yield mock_message
            websocket_client._state = STATE_STOPPED

        mock_ws_client.__aiter__ = lambda self: mock_iter()

        websocket_client.session.ws_connect = MagicMock()
        websocket_client.session.ws_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws_client)
        websocket_client.session.ws_connect.return_value.__aexit__ = AsyncMock()

        websocket_client.websocket_auth = AsyncMock()
        websocket_client.websocket_subscribe = AsyncMock()

        await websocket_client.running()

        # Verify callback was called with the message data
        data_calls = [call for call in mock_callback.call_args_list if call[0][0] == "data"]
        assert len(data_calls) > 0
        assert data_calls[0][0][1] == {"test": "data"}

    @pytest.mark.asyncio
    async def test_running_handles_closed_messages(self, websocket_client):
        """Test that running handles closed messages."""
        mock_ws_client = MagicMock()
        mock_message = MagicMock()
        mock_message.type = WSMsgType.CLOSED

        async def mock_iter():
            yield mock_message

        mock_ws_client.__aiter__ = lambda self: mock_iter()

        websocket_client.session.ws_connect = MagicMock()
        websocket_client.session.ws_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws_client)
        websocket_client.session.ws_connect.return_value.__aexit__ = AsyncMock()

        websocket_client.websocket_auth = AsyncMock()
        websocket_client.websocket_subscribe = AsyncMock()

        with (
            patch("ryobi_gdo_2_mqtt.websocket.log"),
            patch("ryobi_gdo_2_mqtt.websocket.aiohttp.WSMsgType") as mock_wstype,
            patch("ryobi_gdo_2_mqtt.websocket.aiohttp.WSCloseCode") as mock_closecode,
        ):
            mock_wstype.name = "CLOSED"
            mock_closecode.name = "OK"
            await websocket_client.running()

        # Should exit cleanly when connection closes
        assert websocket_client.state == STATE_DISCONNECTED
