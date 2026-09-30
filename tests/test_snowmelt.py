"""Tests for snowmelt mapping helpers and descriptor registry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from homeassistant.const import Platform

from custom_components.watts_home.models import WattsDevice
from custom_components.watts_home.snowmelt_entity import field_is_present
from custom_components.watts_home.snowmelt_mapping import (
    enum_is_switch,
    enum_to_switch_is_on,
    is_enable_active,
    is_melting,
    switch_to_enum_value,
    water_detected,
)
from custom_components.watts_home.snowmelt_registry import (
    SNOWMELT_DESCRIPTORS,
    descriptors_for_platform,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "snowmelt_devices.json"
_STRINGS = (
    Path(__file__).parent.parent / "custom_components" / "watts_home" / "strings.json"
)


@pytest.fixture(name="snowmelt_devices")
def snowmelt_devices_fixture() -> list[WattsDevice]:
    raw = json.loads(_FIXTURE.read_text())["body"]
    return [WattsDevice.model_validate(item) for item in raw]


def test_friendly_names_match_registry() -> None:
    strings = json.loads(_STRINGS.read_text())["entity"]
    platform_map = {
        Platform.SENSOR: "sensor",
        Platform.BINARY_SENSOR: "binary_sensor",
        Platform.NUMBER: "number",
        Platform.SWITCH: "switch",
        Platform.SELECT: "select",
    }
    for descriptor in SNOWMELT_DESCRIPTORS:
        platform_strings = strings[platform_map[descriptor.platform]]
        assert descriptor.key in platform_strings
        assert platform_strings[descriptor.key]["name"] == descriptor.friendly_name


def test_all_descriptors_have_unique_keys() -> None:
    keys = [descriptor.key for descriptor in SNOWMELT_DESCRIPTORS]
    assert len(keys) == len(set(keys))


def test_expected_entity_count_per_device(snowmelt_devices: list[WattsDevice]) -> None:
    device = snowmelt_devices[0]
    present = [
        descriptor
        for descriptor in SNOWMELT_DESCRIPTORS
        if field_is_present(device, descriptor)
    ]
    assert len(present) == 21
    assert len(descriptors_for_platform(Platform.SENSOR)) == 5
    assert len(descriptors_for_platform(Platform.BINARY_SENSOR)) == 2
    assert len(descriptors_for_platform(Platform.NUMBER)) == 8
    assert len(descriptors_for_platform(Platform.SWITCH)) == 4
    assert len(descriptors_for_platform(Platform.SELECT)) == 2


def test_is_melting_manual_melt_from_fixture() -> None:
    raw = json.loads(
        (
            Path(__file__).parent / "fixtures" / "snowmelt_bunkroom_manual_melt.json"
        ).read_text()
    )["body"][0]
    device = WattsDevice.model_validate(raw)
    assert device.data is not None
    assert device.data.melt_man is not None
    assert device.data.melt_man.val == "Melt"
    assert device.data.state is not None
    assert device.data.state.op == "Melt"
    assert device.data.state.sub == "None"
    assert device.data.target is not None
    assert device.data.target.melt_time is not None
    assert device.data.target.melt_time.val == 234
    assert device.data.target.melt_time.status == "Okay"
    assert is_melting(device) is True


def test_water_and_melt_man_helpers(snowmelt_devices: list[WattsDevice]) -> None:
    device = snowmelt_devices[0]
    assert device.data is not None
    assert device.data.sensors is not None
    assert water_detected(device.data.sensors.water) is False
    assert enum_is_switch(device.data.melt_man) is True
    assert enum_to_switch_is_on(device.data.melt_man.val) is False
    assert switch_to_enum_value(True, device.data.melt_man) == "Melt"
    assert enum_is_switch(device.data.wwsd_enable) is False


def test_enable_gating(snowmelt_devices: list[WattsDevice]) -> None:
    device = snowmelt_devices[0]
    assert device.data is not None
    assert is_enable_active(device, "idle_enable") is False
    assert is_enable_active(device, "storm_enable") is False
    assert is_enable_active(device, "cwco_enable") is True
