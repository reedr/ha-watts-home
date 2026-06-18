"""Pure snowmelt data-mapping helpers (no Home Assistant dependency)."""

from __future__ import annotations

from typing import Any

from .models import (
    WattsDevice,
    WattsEnumSetting,
    WattsNumericSetting,
    WattsSensor,
    WattsTargetValue,
)

SWITCH_ON_VALUES = frozenset({"On", "Melt"})
SWITCH_OFF_VALUES = frozenset({"Off", "Stop"})


def snowmelt_temperature_unit(device: WattsDevice) -> str:
    """Return 'F' or 'C' for a snowmelt device."""
    if device.data is None or device.data.temp_units is None:
        return "F"
    return device.data.temp_units.val


def sensor_ok(sensor: WattsSensor | None) -> bool:
    return sensor is not None and sensor.status == "Okay"


def sensor_numeric_value(sensor: WattsSensor | None) -> float | None:
    if not sensor_ok(sensor) or not isinstance(sensor.val, (int, float)):
        return None
    return float(sensor.val)


def water_detected(sensor: WattsSensor | None) -> bool | None:
    if not sensor_ok(sensor) or not isinstance(sensor.val, str):
        return None
    return sensor.val.lower() != "dry"


def is_melting(device: WattsDevice) -> bool | None:
    if device.data is None or device.data.state is None:
        return None
    return device.data.state.op != "Off"


def target_value(target: WattsTargetValue | None) -> float | int | None:
    if target is None:
        return None
    return target.val


def numeric_setting_value(setting: WattsNumericSetting | None) -> float | None:
    if setting is None or setting.val is None:
        return None
    return float(setting.val)


def enum_setting_value(setting: WattsEnumSetting | None) -> str | None:
    if setting is None:
        return None
    return setting.val


def enum_is_switch(setting: WattsEnumSetting | None) -> bool:
    if setting is None or not setting.enum:
        return False
    enum_set = set(setting.enum)
    return enum_set <= (SWITCH_ON_VALUES | SWITCH_OFF_VALUES)


def enum_to_switch_is_on(value: str | None) -> bool | None:
    if value is None:
        return None
    if value in SWITCH_ON_VALUES:
        return True
    if value in SWITCH_OFF_VALUES:
        return False
    return None


def switch_to_enum_value(is_on: bool, setting: WattsEnumSetting) -> str:
    enum = setting.enum or []
    if is_on:
        for candidate in ("Melt", "On"):
            if candidate in enum:
                return candidate
    else:
        for candidate in ("Stop", "Off"):
            if candidate in enum:
                return candidate
    return enum[0]


def get_data_attr(device: WattsDevice, attr: str) -> Any:
    if device.data is None:
        return None
    return getattr(device.data, attr, None)


def is_enable_active(device: WattsDevice, enable_attr: str | None) -> bool:
    if enable_attr is None:
        return True
    enable = get_data_attr(device, enable_attr)
    if not isinstance(enable, WattsEnumSetting):
        return True
    return enable.val in SWITCH_ON_VALUES


def setting_is_available(device: WattsDevice, enable_attr: str | None) -> bool:
    if not device.is_connected:
        return False
    return is_enable_active(device, enable_attr)
