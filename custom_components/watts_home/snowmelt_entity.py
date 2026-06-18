"""Shared snowmelt entity base and platform setup helpers."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, device_model_name
from .coordinator import WattsDataUpdateCoordinator
from .models import WattsDevice
from .snowmelt_mapping import get_data_attr
from .snowmelt_registry import SnowmeltDescriptor, descriptors_for_platform


def snowmelt_device_info(device: WattsDevice) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, device.device_id)},
        name=device.name,
        model=device_model_name(device.model_number),
        manufacturer="Watts Home",
    )


class WattsSnowmeltEntity(CoordinatorEntity[WattsDataUpdateCoordinator]):
    """Base entity for a single snowmelt controller field."""

    def __init__(
        self,
        coordinator: WattsDataUpdateCoordinator,
        device_id: str,
        descriptor: SnowmeltDescriptor,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self.descriptor = descriptor
        device = coordinator.data[device_id]
        self._attr_unique_id = f"{device_id}_{descriptor.key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = descriptor.key
        self._attr_device_info = snowmelt_device_info(device)

    def _device(self) -> WattsDevice:
        return self.coordinator.data[self._device_id]

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        try:
            return self._device().is_connected
        except KeyError:
            return False


def field_is_present(device: WattsDevice, descriptor: SnowmeltDescriptor) -> bool:
    """Return True when the API field exists on this device."""
    if device.data is None:
        return False
    if descriptor.kind == "sensor_reading":
        sensors = device.data.sensors
        if sensors is None or descriptor.sensor_field is None:
            return False
        return getattr(sensors, descriptor.sensor_field, None) is not None
    if descriptor.kind == "target_reading":
        target = device.data.target
        if target is None or descriptor.target_field is None:
            return False
        return getattr(target, descriptor.target_field, None) is not None
    if descriptor.kind == "state_reading":
        state = device.data.state
        if state is None or descriptor.state_field is None:
            return False
        return getattr(state, descriptor.state_field, None) is not None
    if descriptor.data_attr is None:
        return False
    return get_data_attr(device, descriptor.data_attr) is not None


async def async_setup_snowmelt_platform(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    platform: Platform,
    entity_factory: Callable[..., Entity],
) -> None:
    """Create snowmelt entities for one platform from the descriptor registry."""
    coordinator: WattsDataUpdateCoordinator = entry.runtime_data
    known_unique_ids: set[str] = set()

    @callback
    def _async_add_new() -> None:
        new_entities: list[Entity] = []
        for device_id, device in coordinator.data.items():
            if not device.is_snowmelt:
                continue
            for descriptor in descriptors_for_platform(platform):
                unique_id = f"{device_id}_{descriptor.key}"
                if unique_id in known_unique_ids:
                    continue
                if not field_is_present(device, descriptor):
                    continue
                known_unique_ids.add(unique_id)
                new_entities.append(entity_factory(coordinator, device_id, descriptor))
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_async_add_new))
    _async_add_new()
