""" Halo Infinite CSR Sensor """
from datetime import timedelta, timezone
import logging
from typing import Union

import requests.exceptions
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

import voluptuous as vol
from halo_infinite import HaloInfinite, CSREntry
from halo_infinite.match import Match

from .const import (
    DOMAIN,
    CONF_LIST,
    API_VERSION,
    CONTROLLER,
    CROSSPLAY,
    MNK,
    CSR,
    KDR,
    PLAYLISTS,
)

logger = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=20)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                # vol.Required(CONF_NAME): cv.string,
                vol.Required("gamer_tag"): cv.string,
                # vol.Required("season"): cv.string,
                vol.Optional(CONF_LIST, default=PLAYLISTS): vol.All(
                    cv.ensure_list, [cv.string], [vol.In(PLAYLISTS)]
                ),
                # vol.Optional("scan_interval_min", default=30): cv.positive_int
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup for the Halo Infinite Stats component"""
    logger.debug("load halo sensor")
    token = config[DOMAIN].get(CONF_API_KEY)
    gamertag = config[DOMAIN].get("gamer_tag")
    playlists = config[DOMAIN].get(CONF_LIST)
    # season = config.get("season")
    # scan_interval = config[DOMAIN].get("scan_interval_min")
    api = HaloInfinite(gamertag, token, API_VERSION, num_recent_matches=25)

    try:
        data = HaloInfiniteData(api, playlists)
        data.update()
    except requests.exceptions.RequestException:
        msg = """
            Halo Infinite Stats failed to fetch data from Autocode. Check your gamertag, token, and api_version.
        """
        logger.error(msg)
        return False
    hass.data[DOMAIN] = data
    discovery.load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)

    return True


class HaloInfiniteData:
    """Get updated data from Halo api"""
    def __init__(self, api:HaloInfinite, playlists):
        self._api:HaloInfinite = api
        self.playlists = playlists
        self.current_csrs: Union[dict[str,CSREntry], dict[str,None]] = {
            CROSSPLAY: None,
            CONTROLLER: None,
            MNK: None
        }

        self.new_csr = False
        self.new_matches = False
        self.update()


    @property
    def gamertag(self):
        """Return the gamertag from the api"""
        return self._api.gamertag

    @property
    def most_recent_match(self):
        """Return the most recent match pulled via api"""
        if len(self._api.recent_matches) > 0:
            return self._api.recent_matches[0]
        return None


    def get_rank_image_url(self, playlist):
        """Return the rank icon image url for a playlist/input"""
        return self.current_csrs[playlist].current_image_url

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Update the data via api. The results are cached to reduce the polling rate for free accounts"""
        self.new_csr = self._api.update_csr()
        self.current_csrs = {
            CROSSPLAY: self._api.csrs[CROSSPLAY],
            CONTROLLER: self._api.csrs[CONTROLLER],
            MNK: self._api.csrs[MNK]
        }

        self.new_matches = self._api.update_recent_matches()
        # self.current_kdrs = self._get_kdr()
        logger.debug("Halo Infinite Stats fetched some data")

    def get_recent_stats(self, playlist):
        """Return updated attributes calculated from the stored recent matches"""
        matches:list[Match] = [x for x in self._api.recent_matches if x.playlist.input == playlist]
        if len(matches) > 0:
            ret = {
                'kdr': round(sum([m.players[0].kdr for m in matches]) / len(matches), 2),
                'damage_ratio': round(
                    sum(
                        [m.players[0].damage_stats.damage_dealt /
                         m.players[0].damage_stats.damage_taken
                         for m in matches]
                    ) /
                    len(matches), 2
                ),
                'count': len(matches),
                'wins': len([m for m in matches if m.players[0].outcome == 'win']),
                'most_recent': max([m.date_time.replace(tzinfo=timezone.utc).astimezone(tz=None) for m in matches]),
            }
            return ret
        return {
            'kdr': 0,
            'damage_ratio': 0,
            'count': 0,
            'most_recent': None
        }

class HaloInfiniteSensor(Entity):
    """ Implementation of Halo Stats sensor for CSR """

    def __init__(self, halo_data:HaloInfiniteData):
        self.halo_data:HaloInfiniteData = halo_data
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._sensor_type = None
        self._playlist = None

    def update(self):
        """Ask the data handler to update"""
        self.halo_data.update()