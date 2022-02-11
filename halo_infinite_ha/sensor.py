"""
add this to config
sensor:
    - name: halo_infinite_integration
      api_key: <api_token>
      gamer_tag: <gamertag>
      api_version: "0.3.8"
"""

import logging
# import async_timeout

from homeassistant.components.sensor import (
    # PLATFORM_SCHEMA,
    SensorEntity,
    # SensorEntityDescription
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType, ConfigType, DiscoveryInfoType

from . import HaloInfiniteSensor
from .const import (
    DOMAIN,
    SENSOR_TYPES,
    CSR,
    KDR,
    # PLAYLISTS,
    CONTROLLER,
    CROSSPLAY,
    ICONS,
)

# from halo_infinite import HaloInfinite,CSREntry

logger = logging.getLogger(__name__)

DESIRED_PLAYLISTS = [CONTROLLER, CROSSPLAY]

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

    sensors = []
    for s_type in SENSOR_TYPES:
        for p in DESIRED_PLAYLISTS:
            sensors.append(HaloInfiniteStatSensor(data, s_type, p))
    logger.debug("{} Halo sensors generated".format(len(sensors)))
    add_entites(sensors)


class HaloInfiniteStatSensor(HaloInfiniteSensor, SensorEntity):
    def __init__(self, halo_data, sensor_type, playlist):
        HaloInfiniteSensor.__init__(self, halo_data)
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type]

        self._state = None
        self._sensor_type = sensor_type
        self._playlist = playlist

        self.update()

    @property
    def name(self):
        """Return the name of the sensor"""
        return "{} {} {}".format(
            self.halo_data.gamertag, self._playlist, SENSOR_TYPES[self._sensor_type]
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of sensor"""
        return self._state

    @property
    def icon(self):
        """ Return the icon for lovelace """
        return ICONS[self._sensor_type]

    def update(self):
        """Gets the latest api data and update the sensor state"""
        HaloInfiniteSensor.update(self)
        self._state = self.halo_data.get_value(self._sensor_type, self._playlist)