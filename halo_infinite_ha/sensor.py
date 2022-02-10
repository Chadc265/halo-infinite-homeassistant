"""
add this to config
sensor:
    - name: halo_infinite_integration
      api_key: <api_token>
      gamer_tag: <gamertag>
      season: <ranked season>
      api_version: "0.3.8"
"""
from datetime import date, datetime, timedelta
import logging
# import async_timeout

from homeassistant.components.sensor import (
    # PLATFORM_SCHEMA,
    SensorStateClass,
    SensorEntity,
    SensorEntityDescription
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.const import CONF_API_KEY, CONF_NAME
# import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import StateType, ConfigType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    # UpdateFailed,
)

from . import SENSOR_TYPES
from .const import DOMAIN

from halo_infinite import HaloInfinite,CSREntry

logger = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)
# DOMAIN = "sensor"
# API_VERSION = "0.3.8"



async def async_setup_platform(hass:HomeAssistant, config:ConfigEntry, async_add_entities:AddEntitiesCallback, discovery_info=None):
    if discovery_info is None:
        return

    api:HaloInfinite = hass.data[DOMAIN]['api']
    async def async_update_data(ha:HomeAssistant):
        data = await ha.async_add_executor_job(api.update_csr())
        return data
    coordinator = DataUpdateCoordinator(
        hass,
        logger,
        name='sensor',
        update_method=async_update_data,
        update_interval=timedelta(minutes=30)
    )
    await coordinator.async_config_entry_first_refresh()
    async_add_entities(
        [HaloInfiniteSensor(coordinator, des) for des in SENSOR_TYPES],
        True
    )


class HaloInfiniteSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator:DataUpdateCoordinator, description:SensorEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_native_unit_of_measurement = "CSR"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self.data: CSREntry | None = None

    @property
    def native_value(self) -> StateType:
        self.data = self.coordinator.data.data[self.entity_description.key]
        if self.data is not None:
            return self.data.current_value
        return -1

    @property
    def name(self):
        return self.coordinator.data.name
