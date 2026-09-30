"""Number platform for Watts Home thermostats and snowmelt controllers."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, Platform, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helpers import device_model_name
from .coordinator import WattsDataUpdateCoordinator
from .models import WattsDevice, WattsNumericSetting
from .snowmelt_entity import WattsSnowmeltEntity, async_setup_snowmelt_platform
from .snowmelt_mapping import (
    get_data_attr,
    numeric_setting_value,
    setting_is_available,
    snowmelt_temperature_unit,
)
from .snowmelt_registry import SnowmeltDescriptor


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await _async_setup_thermostat_entities(hass, entry, async_add_entities)
    await async_setup_snowmelt_platform(
        hass,
        entry,
        async_add_entities,
        Platform.NUMBER,
        WattsSnowmeltNumber,
    )


async def _async_setup_thermostat_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WattsDataUpdateCoordinator = entry.runtime_data
    known_entity_ids: set[str] = set()

    @callback
    def _async_add_new() -> None:
        new: list[NumberEntity] = []
        for device_id, device in coordinator.data.items():
            if not device.is_thermostat:
                continue
            if device.data and device.data.dehum is not None:
                uid = f"{device_id}_dehum_setpoint"
                if uid not in known_entity_ids:
                    known_entity_ids.add(uid)
                    new.append(WattsDehumSetpointNumber(coordinator, device_id))
        if new:
            async_add_entities(new)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new))
    _async_add_new()


def _device_info(device: WattsDevice) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, device.device_id)},
        name=device.name,
        model=device_model_name(device),
        manufacturer="Watts Home",
    )


class WattsDehumSetpointNumber(
    CoordinatorEntity[WattsDataUpdateCoordinator], NumberEntity
):
    """Dehumidifier target setpoint for a Watts/Tekmar device."""

    _attr_device_class = NumberDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.BOX
    _attr_has_entity_name = True
    _attr_translation_key = "dehumidifier_setpoint"

    def __init__(
        self,
        coordinator: WattsDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_dehum_setpoint"
        device = coordinator.data[device_id]
        self._attr_device_info = _device_info(device)
        dehum = device.data.dehum  # type: ignore[union-attr]
        self._attr_native_min_value = dehum.min
        self._attr_native_max_value = dehum.max
        self._attr_native_step = dehum.steps

    def _device(self) -> WattsDevice:
        return self.coordinator.data[self._device_id]  # KeyError → available=False

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        try:
            d = self._device()
            return d.is_connected and d.data is not None and d.data.dehum is not None
        except KeyError:
            return False

    @property
    def native_value(self) -> float | None:
        d = self._device()
        return d.data.dehum.val if d.data and d.data.dehum else None

    async def async_set_native_value(self, value: float) -> None:
        client = await self.coordinator.async_get_client()
        await client.set_dehumidity_setpoint(self._device_id, value)
        await self.coordinator.async_request_refresh()


class WattsSnowmeltNumber(WattsSnowmeltEntity, NumberEntity):
    """Number mapped from a snowmelt numeric API setting."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator,
        device_id: str,
        descriptor: SnowmeltDescriptor,
    ) -> None:
        super().__init__(coordinator, device_id, descriptor)
        if descriptor.device_class == "temperature":
            self._attr_device_class = NumberDeviceClass.TEMPERATURE
        self._configure_units()

    def _configure_units(self) -> None:
        desc = self.descriptor
        if desc.unit == "temperature":
            device = self.coordinator.data[self._device_id]
            unit = snowmelt_temperature_unit(device)
            self._attr_native_unit_of_measurement = (
                UnitOfTemperature.FAHRENHEIT
                if unit == "F"
                else UnitOfTemperature.CELSIUS
            )
        elif desc.unit == "duration":
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def _setting(self) -> WattsNumericSetting | None:
        setting = get_data_attr(self._device(), self.descriptor.data_attr or "")
        return setting if isinstance(setting, WattsNumericSetting) else None

    @property
    def available(self) -> bool:
        device = self._device()
        if not setting_is_available(device, self.descriptor.requires_enable_attr):
            return False
        return super().available and self._setting() is not None

    @property
    def native_value(self) -> float | None:
        return numeric_setting_value(self._setting())

    @property
    def native_min_value(self) -> float:
        setting = self._setting()
        if setting is None or setting.min is None:
            return 0.0
        return float(setting.min)

    @property
    def native_max_value(self) -> float:
        setting = self._setting()
        if setting is None or setting.max is None:
            return 100.0
        return float(setting.max)

    @property
    def native_step(self) -> float:
        setting = self._setting()
        if setting is None or setting.steps is None:
            return 1.0
        return float(setting.steps)

    async def async_set_native_value(self, value: float) -> None:
        client = await self.coordinator.async_get_client()
        await client.set_setting(self._device_id, self.descriptor.api_key, value)
        await self.coordinator.async_request_refresh()
