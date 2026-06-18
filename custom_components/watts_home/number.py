"""Number platform for Watts Home snowmelt controllers."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .models import WattsNumericSetting
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
    await async_setup_snowmelt_platform(
        hass,
        entry,
        async_add_entities,
        Platform.NUMBER,
        WattsSnowmeltNumber,
    )


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
