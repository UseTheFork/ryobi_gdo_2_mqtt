import asyncio
import sys

from ryobi_gdo_2_mqtt.logging import log
from ryobi_gdo_2_mqtt.settings import Settings


class RyobiGDO2MQTT:
    """RyobiGDO 2 MQTT service."""

    def __call__(self, settings: Settings) -> None:
        """Start the RyobiGDO 2 MQTT service."""
        try:
            asyncio.run(self._run(settings))
        except Exception as ex:
            log.critical("Unhandled exception occured, exiting")
            log.critical(ex)
            sys.exit()

    async def _run(self, settings: Settings) -> None:
        """Run the main async logic."""
        pass


ryobi_gdo2_mqtt = RyobiGDO2MQTT()
