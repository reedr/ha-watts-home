"""Declarative registry of snowmelt API fields to Home Assistant entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from homeassistant.const import Platform

SnowmeltKind = Literal[
    "sensor_reading",
    "target_reading",
    "state_reading",
    "numeric",
    "enum",
]


@dataclass(frozen=True, slots=True)
class SnowmeltDescriptor:
    """Maps one snowmelt API field to a Home Assistant entity."""

    key: str
    api_key: str
    friendly_name: str
    platform: Platform
    kind: SnowmeltKind
    data_attr: str | None = None
    sensor_field: str | None = None
    target_field: str | None = None
    state_field: str | None = None
    requires_enable_attr: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    unit: Literal["temperature", "duration", "none"] = "none"


SNOWMELT_DESCRIPTORS: tuple[SnowmeltDescriptor, ...] = (
    SnowmeltDescriptor(
        key="outdoor",
        api_key="Outdoor",
        friendly_name="Outdoor Temperature",
        platform=Platform.SENSOR,
        kind="sensor_reading",
        sensor_field="outdoor",
        device_class="temperature",
        state_class="measurement",
        unit="temperature",
    ),
    SnowmeltDescriptor(
        key="slab_temperature",
        api_key="Slab",
        friendly_name="Slab Temperature",
        platform=Platform.SENSOR,
        kind="sensor_reading",
        sensor_field="slab",
        device_class="temperature",
        state_class="measurement",
        unit="temperature",
    ),
    SnowmeltDescriptor(
        key="water",
        api_key="Water",
        friendly_name="Water Detected",
        platform=Platform.BINARY_SENSOR,
        kind="sensor_reading",
        sensor_field="water",
        device_class="moisture",
    ),
    SnowmeltDescriptor(
        key="melting",
        api_key="Op",
        friendly_name="Melting Active",
        platform=Platform.BINARY_SENSOR,
        kind="state_reading",
        state_field="op",
        device_class="heat",
    ),
    SnowmeltDescriptor(
        key="status_reason",
        api_key="Sub",
        friendly_name="Status Reason",
        platform=Platform.SENSOR,
        kind="state_reading",
        state_field="sub",
    ),
    SnowmeltDescriptor(
        key="target_slab",
        api_key="Slab",
        friendly_name="Slab Target",
        platform=Platform.SENSOR,
        kind="target_reading",
        target_field="slab",
    ),
    SnowmeltDescriptor(
        key="melt_time_remaining",
        api_key="MeltTime",
        friendly_name="Melt Time Remaining",
        platform=Platform.SENSOR,
        kind="target_reading",
        target_field="melt_time",
        state_class="measurement",
        unit="duration",
    ),
    SnowmeltDescriptor(
        key="melt_temperature",
        api_key="Melt",
        friendly_name="Melting Setpoint",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="melt",
        device_class="temperature",
        unit="temperature",
    ),
    SnowmeltDescriptor(
        key="manual_melt",
        api_key="MeltMan",
        friendly_name="Manual Melt",
        platform=Platform.SWITCH,
        kind="enum",
        data_attr="melt_man",
    ),
    SnowmeltDescriptor(
        key="manual_melt_time",
        api_key="MeltManTime",
        friendly_name="Manual Melt Duration",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="melt_man_time",
        unit="duration",
    ),
    SnowmeltDescriptor(
        key="melt_add_time",
        api_key="MeltAddTime",
        friendly_name="Additional Melt Time",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="melt_add_time",
        unit="duration",
    ),
    SnowmeltDescriptor(
        key="idle_enable",
        api_key="IdleEnable",
        friendly_name="Idle Enabled",
        platform=Platform.SWITCH,
        kind="enum",
        data_attr="idle_enable",
    ),
    SnowmeltDescriptor(
        key="idle_temperature",
        api_key="Idle",
        friendly_name="Idle Setpoint",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="idle",
        requires_enable_attr="idle_enable",
        device_class="temperature",
        unit="temperature",
    ),
    SnowmeltDescriptor(
        key="storm_enable",
        api_key="StormEnable",
        friendly_name="Storm Enabled",
        platform=Platform.SWITCH,
        kind="enum",
        data_attr="storm_enable",
    ),
    SnowmeltDescriptor(
        key="storm_temperature",
        api_key="Storm",
        friendly_name="Storm Setpoint",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="storm",
        requires_enable_attr="storm_enable",
        device_class="temperature",
        unit="temperature",
    ),
    SnowmeltDescriptor(
        key="storm_run_time",
        api_key="StormRunTime",
        friendly_name="Storm Run Duration",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="storm_run_time",
        requires_enable_attr="storm_enable",
        unit="duration",
    ),
    SnowmeltDescriptor(
        key="wwsd_enable",
        api_key="WWSDEnable",
        friendly_name="Warm Weather Shutoff Mode",
        platform=Platform.SELECT,
        kind="enum",
        data_attr="wwsd_enable",
    ),
    SnowmeltDescriptor(
        key="wwsd_temperature",
        api_key="WWSD",
        friendly_name="Warm Weather Shutoff Setpoint",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="wwsd",
        device_class="temperature",
        unit="temperature",
    ),
    SnowmeltDescriptor(
        key="cwco_enable",
        api_key="CWCOEnable",
        friendly_name="Cold Weather Cutoff Enabled",
        platform=Platform.SWITCH,
        kind="enum",
        data_attr="cwco_enable",
    ),
    SnowmeltDescriptor(
        key="cwco_temperature",
        api_key="CWCO",
        friendly_name="Cold Weather Cutoff Setpoint",
        platform=Platform.NUMBER,
        kind="numeric",
        data_attr="cwco",
        requires_enable_attr="cwco_enable",
        device_class="temperature",
        unit="temperature",
    ),
    SnowmeltDescriptor(
        key="sensitivity",
        api_key="Sensitivity",
        friendly_name="Melt Sensitivity",
        platform=Platform.SELECT,
        kind="enum",
        data_attr="sensitivity",
    ),
)


def descriptors_for_platform(platform: Platform) -> tuple[SnowmeltDescriptor, ...]:
    return tuple(d for d in SNOWMELT_DESCRIPTORS if d.platform == platform)
