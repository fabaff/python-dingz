"""A Python Client to interact with Dingz devices."""
import logging

import aiohttp
from yarl import URL

from . import make_call
from .constants import (
    API,
    BUTTON_ACTIONS,
    DEVICE_INFO,
    FRONT_LED_GET,
    FRONT_LED_SET,
    INPUT_CONFIGURATION,
    LIGHT,
    PIR_CONFIGURATION,
    PUCK,
    SETTINGS,
    TEMPERATURE,
    THERMOSTAT_CONFIGURATION,
)

_LOGGER = logging.getLogger(__name__)


class Dingz:
    """A class for handling the communication with a dingz device."""

    def __init__(self, host: str, session: aiohttp.client.ClientSession = None) -> None:
        """Initialize the dingz."""
        self._close_session = False
        self._host = host
        self._session = session
        self._device_details = None
        self._catch_all = {}
        self._button_action = None
        self._temperature = None
        self._intensity = None
        self._day = None
        self._night = None
        self._hour_of_day = None
        self.uri = URL.build(scheme="http", host=self._host).join(URL(API))

    async def get_device_info(self) -> None:
        """Get the details from the dingz."""
        url = URL(self.uri).join(URL(DEVICE_INFO))
        response = await make_call(self, uri=url)
        self._device_details = response

    async def get_info(self) -> None:
        """Get everything from the dingz unit."""
        for endpoint in [
            PUCK,
            DEVICE_INFO,
            SETTINGS,
            PIR_CONFIGURATION,
            THERMOSTAT_CONFIGURATION,
            INPUT_CONFIGURATION,
            BUTTON_ACTIONS,
        ]:
            url = URL(self.uri).join(URL(endpoint))
            self._catch_all[endpoint] = await make_call(self, uri=url)

    async def get_temperature(self) -> None:
        """Get the room temperature from the dingz."""
        url = URL(self.uri).join(URL(TEMPERATURE))
        response = await make_call(self, uri=url)
        self._temperature = response["temperature"]

    async def get_button_action(self) -> None:
        """Get the room temperature from the dingz."""
        url = URL(self.uri).join(URL(BUTTON_ACTIONS))
        self._button_action = await make_call(self, uri=url)

    async def get_light(self) -> None:
        """Get the light details from the switch."""
        url = URL(self.uri).join(URL(LIGHT))
        response = await make_call(self, uri=url)
        print(response)
        self._intensity = response["intensity"]
        self._hour_of_day = response["state"]

    async def enabled(self) -> bool:
        """Return true if front LED is on."""
        url = URL(self.uri).join(URL(FRONT_LED_GET))
        response = await make_call(self, uri=url)
        return bool(response["on"])

    async def turn_on(self) -> None:
        """Enable/turn on the front LED."""
        data = {"action": "on"}
        url = URL(self.uri).join(URL(FRONT_LED_SET))
        await make_call(self, uri=url, method="POST", data=data)

    async def turn_off(self) -> None:
        """Disable/turn off the front LED."""
        data = {"action": "off"}
        url = URL(self.uri).join(URL(FRONT_LED_SET))
        await make_call(self, uri=url, method="POST", data=data)

    @property
    def device_details(self) -> str:
        """Return the current device details."""
        return self._device_details

    @property
    def everything(self) -> str:
        """Return the all available device details."""
        return self._catch_all

    @property
    def button_action(self) -> float:
        """Return the current button action."""
        return self._button_action

    @property
    def temperature(self) -> float:
        """Return the current temperature in celsius."""
        return round(self._temperature, 1)

    @property
    def day(self) -> bool:
        """Return true if the sensor thinks it's day."""
        return True if self._hour_of_day == "day" else False

    @property
    def night(self) -> bool:
        """Return true if the sensor thinks it's night."""
        return True if self._hour_of_day == "night" else False

    @property
    def intensity(self) -> float:
        """Return the current light intensity in lux."""
        return round(self._intensity, 1)

    # See "Using Asyncio in Python" by Caleb Hattingh for implementation
    # details.
    async def close(self) -> None:
        """Close an open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "Dingz":
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
