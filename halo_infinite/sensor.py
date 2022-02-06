"""
add this to config
sensor:
    - name: halo_infinite_integration
      api_key: <api_token>
      gamer_tag: <gamertag>
      season: <ranked season>
      api_version: "0.3.8"
"""
import logging
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import voluptuous as vol

from halo_infinite import HaloInfinite, CSR, CSREntry

logger = logging.getLogger(__name__)

DOMAIN = "sensor"
API_VERSION = "0.3.8"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required("gamer_tag"): cv.string,
        vol.Required("season"): cv.string,
        vol.Required("api_version"): cv.string
    }
)

def setup_platform(hass:HomeAssistant, config, add_entities:AddEntitiesCallback, discovery_info=None):
    logger.info("load halo sensor")
    token = config.get(CONF_API_KEY)
    name = config.get(CONF_NAME)
    gamertag = config.get("gamer_tag")
    season = config.get("season")
    api_version = config.get("api_version")

    halo = HaloInfinite(name, gamertag, token, season, api_version)
    if not halo:
        logger.error("Could not make connection to halo api")
        return
    add_entities([HaloInfiniteSensor(hass, halo)], True)

class HaloInfiniteSensor(Entity):
    def __init__(self, hass:HomeAssistant, halo:HaloInfinite):
        self._hass = hass
        self.data:HaloInfinite = halo

    @property
    def name(self):
        return self.data.name

    @property
    def state(self):
        csr = self.data.update_csr()
        cp:CSREntry = csr['crossplay']
        return cp.current_value

