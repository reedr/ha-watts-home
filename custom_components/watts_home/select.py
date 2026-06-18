"""Select platform for Watts Home snowmelt controllers."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .models import WattsEnumSetting
from .snowmelt_entity import WattsSnowmeltEntity, async_setup_snowmelt_platform
from .snowmelt_mapping import enum_is_switch, enum_setting_value, get_data_attr
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
        Platform.SELECT,
        WattsSnowmeltSelect,
    )


class WattsSnowmeltSelect(WattsSnowmeltEntity, SelectEntity):
    """Select mapped from a snowmelt enum setting with more than two options."""

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
        setting = self._setting()
        if setting is None or enum_is_switch(setting):
            return False
        return super().available

    @property
    def options(self) -> list[str]:
        setting = self._setting()
        return list(setting.enum) if setting and setting.enum else []

    @property
    def current_option(self) -> str | None:
        return enum_setting_value(self._setting())

    async def async_select_option(self, option: str) -> None:
        client = await self.coordinator.async_get_client()
        await client.set_setting(self._device_id, self.descriptor.api_key, option)
        await self.coordinator.async_request_refresh()
