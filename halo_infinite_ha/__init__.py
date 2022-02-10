""" Halo Infinite CSR Sensor """
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntityDescription
import voluptuous as vol

from halo_infinite import HaloInfinite

from .const import DOMAIN

logger = logging.getLogger(__name__)

PLATFORMS = ['sensor']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required("gamer_tag"): cv.string,
        vol.Required("season"): cv.string,
        vol.Required("api_version"): cv.string
    }
)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="crossplay",
        name="crossplay",
        icon="mdi:arrow-top-left-bottom-right"
    ),
    SensorEntityDescription(
        key='controller',
        name='controller',
        icon='mdi:microsoft-xbox-controller'
    )
)

async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Your controller/hub specific code."""
    logger.info("load halo sensor")
    token = config.data.get(CONF_API_KEY)
    name = config.data.get(CONF_NAME)
    gamertag = config.data.get("gamer_tag")
    season = config.data.get("season")
    api_version = config.data.get("api_version")

    halo = HaloInfinite(name, gamertag, token, season, api_version)
    if not halo:
        logger.error("Could not make connection to halo api")
        return False
    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {
        'api': halo
    }
    hass.config_entries.async_setup_platforms(config, PLATFORMS)
    return True
