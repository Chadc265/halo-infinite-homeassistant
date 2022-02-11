""" Halo Infinite CSR Sensor """
from datetime import timedelta
import logging

import requests.exceptions
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

import voluptuous as vol
from halo_infinite import HaloInfinite
# from halo_infinite.match import Match
# from halo_infinite.player import PlayerMatchStats

from .const import (
    DOMAIN,
    CONTROLLER,
    CROSSPLAY,
    MNK,
    CURRENT,
    RECENT_CHANGE
)

logger = logging.getLogger(__name__)

# PLATFORMS = ['sensor']
SCAN_INTERVAL = timedelta(minutes=30)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                # vol.Required(CONF_NAME): cv.string,
                vol.Required("gamer_tag"): cv.string,
                # vol.Required("season"): cv.string,
                vol.Required("api_version"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

# SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
#     SensorEntityDescription(
#         key="crossplay",
#         name="crossplay",
#         icon="mdi:arrow-top-left-bottom-right"
#     ),
#     SensorEntityDescription(
#         key='controller',
#         name='controller',
#         icon='mdi:microsoft-xbox-controller'
#     )
# )

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup for the Halo Infinite Stats component"""
    logger.debug("load halo sensor")
    token = config[DOMAIN].get(CONF_API_KEY)
    gamertag = config[DOMAIN].get("gamer_tag")
    # season = config.get("season")
    api_version = config[DOMAIN].get("api_version")

    api = HaloInfinite(gamertag, token, api_version)

    try:
        data = HaloInfiniteData(api)
        data.update()
        logger.debug("Halo Infinite Stats fetched some data")
    except requests.exceptions.RequestException:
        msg = """
            Halo Infinite Stats failed to fetch data from Autocode. Check your gamertag, token, and api_version.
        """
        logger.error(msg)
        return False
    hass.data[DOMAIN] = data
    """Crossplay csr sensor"""
    discovery.load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)
    # discovery.load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)

    return True


class HaloInfiniteData:
    """Get updated data from Halo api"""
    def __init__(self, api:HaloInfinite):
        self._api:HaloInfinite = api
        self.current_csrs = {
            CROSSPLAY: -1,
            CONTROLLER: -1,
            MNK: -1
        }
        self.csr_changes = {}
        self.new_csr = False
        self.new_matches = False
        self.update()

    @property
    def gamertag(self):
        return self._api.gamertag

    def get_csr(self, sensor_type, playlist):
        if sensor_type == CURRENT:
            return self.current_csrs[playlist]

        if sensor_type == RECENT_CHANGE:
            return self.csr_changes[playlist]

        logger.debug("Sensor type {} is not valid".format(sensor_type))
        return -1

    @Throttle(SCAN_INTERVAL)
    def update(self):
        self.new_csr = self._api.update_csr()
        self.current_csrs = {
            CROSSPLAY: self._api.csrs[CROSSPLAY].current_value,
            CONTROLLER: self._api.csrs[CONTROLLER].current_value,
            MNK: self._api.csrs[MNK].current_value
        }

        self.new_matches = self._api.update_recent_matches()
        self.csr_changes = self._get_csr_change()
        logger.warning("Halo Infinite Stats fetched some data")

    def _get_csr_change(self):
        if len(self._api.recent_matches) < 1:
            return {CROSSPLAY: 0, CONTROLLER: 0, MNK: 0}
        recent_csrs = {
            CROSSPLAY: [x.players[0].before_csr for x in self._api.recent_matches if x.playlist.input == CROSSPLAY],
            CONTROLLER: [x.players[0].before_csr for x in self._api.recent_matches if x.playlist.input == CONTROLLER],
            MNK: [x.players[0].before_csr for x in self._api.recent_matches if x.playlist.input == MNK]
        }
        ret = {}
        for p in [CROSSPLAY, CONTROLLER, MNK]:
            if self.current_csrs[p] < 0:
                ret[p] = 0
            elif len(recent_csrs[p]) > 0:
                ret[p] = self.current_csrs[p] - recent_csrs[p][-1]
            else:
                ret[p] = 0
        return ret

class HaloInfiniteSensor(Entity):
    """ Implementation of Halo Stats sensor for CSR """

    def __init__(self, halo_data:HaloInfiniteData):
        self.halo_data:HaloInfiniteData = halo_data

        self._sensor_type = None
        self._playlist = None

    def update(self):
        self.halo_data.update()