"""
add this to config
sensor:
      api_key: <api_token>
      gamer_tag: <gamertag>
      ranked_inputs:
        - crossplay
        - controller
        - mnk
"""

import logging
from typing import Union

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType, ConfigType

from halo_infinite.match import Match

from . import HaloInfiniteSensor
from .const import (
    DOMAIN,
    SENSOR_TYPES,
    CSR,
    MATCH,
    ICONS,
)

logger = logging.getLogger(__name__)

def setup_platform(
        hass:HomeAssistant,
        config:ConfigType,
        add_entites:AddEntitiesCallback,
        discovery_info = None,
) -> None:
    if discovery_info is None:
        return

    data = hass.data[DOMAIN]
    data.update()
    playlists = data.playlists
    sensors = []
    for p in playlists:
        sensors.append(HaloInfiniteStatSensor(data, p))
    sensors.append(HaloInfiniteMatchSensor(data))
    logger.debug("{n_sensors} Halo sensors generated".format(n_sensors=len(sensors)))
    add_entites(sensors)


class HaloInfiniteStatSensor(HaloInfiniteSensor, SensorEntity):
    """Sensor to track Halo Infinite CSR with attributes for recent statistics"""
    def __init__(self, halo_data, playlist):
        HaloInfiniteSensor.__init__(self, halo_data)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = SENSOR_TYPES[CSR]
        self._state = None
        self._playlist = playlist
        self._attr_extra_state_attributes = {}
        self.update()

    @property
    def name(self):
        """Return the name of the sensor"""
        return "{tag} {playlist}".format(
            tag=self.halo_data.gamertag, playlist=self._playlist
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of sensor"""
        return self._state

    @property
    def extra_state_attributes(self):
        """Returns the extra attributes"""
        return self._attr_extra_state_attributes

    @property
    def entity_picture(self):
        """Return the picture url if one exists"""
        return self.halo_data.get_rank_image_url(self._playlist)

    def update(self):
        """Gets the latest api data and updates the sensor state"""
        HaloInfiniteSensor.update(self)
        self._state = self.halo_data.current_csrs[self._playlist].current_value
        self._attr_extra_state_attributes = self.halo_data.get_recent_stats(self._playlist)

class HaloInfiniteMatchSensor(HaloInfiniteSensor, SensorEntity):
    """Sensor to show most recent match with stats for players"""
    def __init__(self, halo_data):
        HaloInfiniteSensor.__init__(self, halo_data)
        self._attr_native_unit_of_measurement = SENSOR_TYPES[MATCH]
        self._state = None
        self._attr_extra_state_attributes = {}
        self._recent_match:Union[Match,None] = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor"""
        return "{tag} Last Match".format(
            tag=self.halo_data.gamertag
        )

    @property
    def icon(self):
        """Return the icon for a match"""
        if self._recent_match is None:
            return ICONS[MATCH]
        icon = ICONS[self._recent_match.mode]
        if len(self._recent_match.players) < 1:
            return icon
        if self._attr_extra_state_attributes['outcome'] == 'left':
            return ICONS['left']
        if self._attr_extra_state_attributes['outcome'] == 'loss':
            return icon + "-outline"
        return icon

    @property
    def native_value(self) -> StateType:
        """Return the state of sensor"""
        return self._state

    @property
    def extra_state_attributes(self):
        """Returns the extra attributes"""
        return self._attr_extra_state_attributes

    def update(self):
        """Gets the latest api data and updates the sensor state"""
        HaloInfiniteSensor.update(self)
        self._recent_match:Match = self.halo_data.most_recent_match
        self._state = self._recent_match.date_time
        self._attr_extra_state_attributes = self._get_state_attr()

    def _get_state_attr(self):
        if self._recent_match is None:
            return {}
        if len(self._recent_match.players) < 1:
            return {}
        ret = {
            'mode': self._recent_match.mode,
            'map': self._recent_match.map,
            'input': self._recent_match.playlist.input,
            'duration': self._recent_match.duration_seconds
        }
        player_stats = self._recent_match.players[0].to_dict(False)
        player_stats.pop("player_match_id")
        player_stats.pop("match_completed")
        return {**ret, **player_stats}
