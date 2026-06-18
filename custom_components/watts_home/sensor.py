"""Sensor platform for the Watts Home (Tekmar) integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, Platform, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, device_model_name
from .coordinator import WattsDataUpdateCoordinator
from .models import WattsDevice, WattsSensor
from .snowmelt_entity import WattsSnowmeltEntity, async_setup_snowmelt_platform
from .snowmelt_mapping import (
    sensor_numeric_value,
    sensor_ok,
    snowmelt_temperature_unit,
    target_value,
)
from .snowmelt_registry import SnowmeltDescriptor


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await _async_setup_thermostat_sensors(hass, entry, async_add_entities)
    await async_setup_snowmelt_platform(
        hass,
        entry,
        async_add_entities,
        Platform.SENSOR,
        WattsSnowmeltSensor,
    )


async def _async_setup_thermostat_sensors(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WattsDataUpdateCoordinator = entry.runtime_data
    known_entity_ids: set[str] = set()

    @callback
    def _async_add_new() -> None:
        new: list[SensorEntity] = []
        for device_id, device in coordinator.data.items():
            if not device.is_thermostat:
                continue
            s = device.data.sensors if device.data else None
            if s and s.room and s.room.status == "Okay":
                uid = f"{device_id}_room_temp"
                if uid not in known_entity_ids:
                    known_entity_ids.add(uid)
                    new.append(WattsRoomTempSensor(coordinator, device_id))
            if s and s.outdoor and s.outdoor.status == "Okay":
                uid = f"{device_id}_outdoor_temp"
                if uid not in known_entity_ids:
                    known_entity_ids.add(uid)
                    new.append(WattsOutdoorTempSensor(coordinator, device_id))
            if s and s.rh and s.rh.status == "Okay":
                uid = f"{device_id}_humidity"
                if uid not in known_entity_ids:
                    known_entity_ids.add(uid)
                    new.append(WattsHumiditySensor(coordinator, device_id))
        if new:
            async_add_entities(new)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new))
    _async_add_new()


def _device_info(device: WattsDevice) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, device.device_id)},
        name=device.name,
        model=device_model_name(device.model_number),
        manufacturer="Watts Home",
    )


class WattsRoomTempSensor(CoordinatorEntity[WattsDataUpdateCoordinator], SensorEntity):
    """Room (indoor) temperature sensor for a Watts/Tekmar device.

    Mirrors the climate entity's current temperature as a standalone sensor so
    it gets long-term statistics, which climate entities do not produce.
    """

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_translation_key = "temperature"

    def __init__(
        self,
        coordinator: WattsDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_room_temp"
        device = coordinator.data[device_id]
        self._attr_device_info = _device_info(device)
        unit = (
            device.data.temp_units.val
            if device.data and device.data.temp_units
            else None
        )
        self._attr_native_unit_of_measurement = (
            UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS
        )

    def _device(self) -> WattsDevice:
        return self.coordinator.data[self._device_id]  # KeyError → available=False

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        try:
            d = self._device()
            s = d.data.sensors if d.data else None
            return (
                d.is_connected
                and s is not None
                and s.room is not None
                and s.room.status == "Okay"
            )
        except KeyError:
            return False

    @property
    def native_value(self) -> float | None:
        d = self._device()
        s = d.data.sensors if d.data else None
        if s and s.room and s.room.status == "Okay":
            return s.room.val
        return None


class WattsOutdoorTempSensor(
    CoordinatorEntity[WattsDataUpdateCoordinator], SensorEntity
):
    """Outdoor temperature sensor for a Watts/Tekmar device."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_translation_key = "outdoor_temperature"

    def __init__(
        self,
        coordinator: WattsDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_outdoor_temp"
        device = coordinator.data[device_id]
        self._attr_device_info = _device_info(device)
        unit = (
            device.data.temp_units.val
            if device.data and device.data.temp_units
            else None
        )
        self._attr_native_unit_of_measurement = (
            UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS
        )

    def _device(self) -> WattsDevice:
        return self.coordinator.data[self._device_id]  # KeyError → available=False

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        try:
            d = self._device()
            s = d.data.sensors if d.data else None
            return (
                d.is_connected
                and s is not None
                and s.outdoor is not None
                and s.outdoor.status == "Okay"
            )
        except KeyError:
            return False

    @property
    def native_value(self) -> float | None:
        d = self._device()
        s = d.data.sensors if d.data else None
        if s and s.outdoor and s.outdoor.status == "Okay":
            return s.outdoor.val
        return None


class WattsHumiditySensor(CoordinatorEntity[WattsDataUpdateCoordinator], SensorEntity):
    """Relative humidity sensor for a Watts/Tekmar device."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_has_entity_name = True
    _attr_translation_key = "humidity"

    def __init__(
        self,
        coordinator: WattsDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_humidity"
        self._attr_device_info = _device_info(coordinator.data[device_id])

    def _device(self) -> WattsDevice:
        return self.coordinator.data[self._device_id]  # KeyError → available=False

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        try:
            d = self._device()
            s = d.data.sensors if d.data else None
            return (
                d.is_connected
                and s is not None
                and s.rh is not None
                and s.rh.status == "Okay"
            )
        except KeyError:
            return False

    @property
    def native_value(self) -> float | None:
        d = self._device()
        s = d.data.sensors if d.data else None
        if s and s.rh and s.rh.status == "Okay":
            return s.rh.val
        return None


class WattsSnowmeltSensor(WattsSnowmeltEntity, SensorEntity):
    """Read-only sensor derived from a snowmelt API field."""

    def __init__(
        self,
        coordinator: WattsDataUpdateCoordinator,
        device_id: str,
        descriptor: SnowmeltDescriptor,
    ) -> None:
        super().__init__(coordinator, device_id, descriptor)
        if descriptor.device_class == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        if descriptor.state_class == "measurement":
            self._attr_state_class = SensorStateClass.MEASUREMENT
        if descriptor.unit == "temperature":
            device = coordinator.data[device_id]
            unit = snowmelt_temperature_unit(device)
            self._attr_native_unit_of_measurement = (
                UnitOfTemperature.FAHRENHEIT
                if unit == "F"
                else UnitOfTemperature.CELSIUS
            )
        elif descriptor.unit == "duration":
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES

    @property
    def native_value(self) -> float | str | None:
        device = self._device()
        desc = self.descriptor
        if desc.kind == "sensor_reading":
            sensors = device.data.sensors if device.data else None
            if sensors is None or desc.sensor_field is None:
                return None
            sensor: WattsSensor | None = getattr(sensors, desc.sensor_field, None)
            if desc.sensor_field in {"outdoor", "slab"}:
                return sensor_numeric_value(sensor)
            return sensor.val if sensor is not None else None
        if desc.kind == "target_reading":
            target = device.data.target if device.data else None
            if target is None or desc.target_field is None:
                return None
            return target_value(getattr(target, desc.target_field, None))
        if desc.kind == "state_reading":
            state = device.data.state if device.data else None
            if state is None or desc.state_field is None:
                return None
            return getattr(state, desc.state_field, None)
        return None

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        device = self._device()
        desc = self.descriptor
        if desc.kind == "sensor_reading" and desc.sensor_field in {"outdoor", "slab"}:
            sensors = device.data.sensors if device.data else None
            if sensors is None or desc.sensor_field is None:
                return False
            sensor = getattr(sensors, desc.sensor_field, None)
            return sensor_ok(sensor)
        return True
