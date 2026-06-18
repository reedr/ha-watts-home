"""Binary sensor platform for Watts Home snowmelt controllers."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .snowmelt_entity import WattsSnowmeltEntity, async_setup_snowmelt_platform
from .snowmelt_mapping import (
    is_melting,
    sensor_ok,
    water_detected,
)
from .snowmelt_registry import SnowmeltDescriptor


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await async_setup_snowmelt_platform(
        hass,
        entry,
        async_add_entities,
        Platform.BINARY_SENSOR,
        WattsSnowmeltBinarySensor,
    )


class WattsSnowmeltBinarySensor(WattsSnowmeltEntity, BinarySensorEntity):
    """Binary sensor derived from a snowmelt API field."""

    def __init__(
        self,
        coordinator,
        device_id: str,
        descriptor: SnowmeltDescriptor,
    ) -> None:
        super().__init__(coordinator, device_id, descriptor)
        if descriptor.device_class == "heat":
            self._attr_device_class = BinarySensorDeviceClass.HEAT
        elif descriptor.device_class == "moisture":
            self._attr_device_class = BinarySensorDeviceClass.MOISTURE

    @property
    def is_on(self) -> bool | None:
        device = self._device()
        desc = self.descriptor
        if desc.kind == "sensor_reading" and desc.sensor_field == "water":
            sensors = device.data.sensors if device.data else None
            water = sensors.water if sensors is not None else None
            return water_detected(water)
        if desc.kind == "state_reading" and desc.state_field == "op":
            return is_melting(device)
        return None

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        device = self._device()
        desc = self.descriptor
        if desc.kind == "sensor_reading" and desc.sensor_field == "water":
            sensors = device.data.sensors if device.data else None
            water = sensors.water if sensors is not None else None
            return sensor_ok(water)
        return True
