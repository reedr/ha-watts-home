"""Switch platform for Watts Home snowmelt controllers."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .models import WattsEnumSetting
from .snowmelt_entity import WattsSnowmeltEntity, async_setup_snowmelt_platform
from .snowmelt_mapping import (
    enum_is_switch,
    enum_setting_value,
    enum_to_switch_is_on,
    get_data_attr,
    switch_to_enum_value,
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
        Platform.SWITCH,
        WattsSnowmeltSwitch,
    )


class WattsSnowmeltSwitch(WattsSnowmeltEntity, SwitchEntity):
    """Switch mapped from a snowmelt On/Off or Stop/Melt enum setting."""

    def __init__(
        self,
        coordinator,
        device_id: str,
        descriptor: SnowmeltDescriptor,
    ) -> None:
        super().__init__(coordinator, device_id, descriptor)

    def _setting(self) -> WattsEnumSetting | None:
        setting = get_data_attr(self._device(), self.descriptor.data_attr or "")
        return setting if isinstance(setting, WattsEnumSetting) else None

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        setting = self._setting()
        return setting is not None and enum_is_switch(setting)

    @property
    def is_on(self) -> bool | None:
        setting = self._setting()
        if setting is None:
            return None
        return enum_to_switch_is_on(enum_setting_value(setting))

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_set_switch(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_set_switch(False)

    async def _async_set_switch(self, is_on: bool) -> None:
        setting = self._setting()
        if setting is None:
            return
        value = switch_to_enum_value(is_on, setting)
        client = await self.coordinator.async_get_client()
        await client.set_setting(self._device_id, self.descriptor.api_key, value)
        await self.coordinator.async_request_refresh()
