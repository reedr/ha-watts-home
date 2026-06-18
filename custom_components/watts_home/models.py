"""Pydantic v2 models for Watts Home API device responses."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from .const import (
    DEVICE_TYPE_SNOWMELT,
    DEVICE_TYPE_THERMOSTAT,
    SNOWMELT_MODEL_NUMBERS,
    THERMOSTAT_MODEL_NUMBERS,
)


class WattsDeviceKind(StrEnum):
    """High-level device category derived from API metadata."""

    THERMOSTAT = "thermostat"
    SNOWMELT = "snowmelt"
    UNKNOWN = "unknown"


class WattsSensor(BaseModel):
    """Temperature, humidity, or status sensor reading."""

    model_config = ConfigDict(extra="ignore")

    val: float | str = Field(alias="Val")
    status: str = Field(alias="Status")
    state: str | None = Field(None, alias="State")


class WattsSensors(BaseModel):
    """Sensor group — thermostats use Room/Floor/Outdoor/RH; snowmelt adds Slab/Water."""

    model_config = ConfigDict(extra="ignore")

    room: WattsSensor | None = Field(None, alias="Room")
    floor: WattsSensor | None = Field(None, alias="Floor")
    outdoor: WattsSensor | None = Field(None, alias="Outdoor")
    rh: WattsSensor | None = Field(None, alias="RH")
    slab: WattsSensor | None = Field(None, alias="Slab")
    water: WattsSensor | None = Field(None, alias="Water")


class WattsState(BaseModel):
    """Operational state. Thermostats use Op=Heat/Cool/Off; snowmelt uses Sub for reason."""

    model_config = ConfigDict(extra="ignore")

    op: str = Field(alias="Op")
    sub: str | None = Field(None, alias="Sub")


class WattsMode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    val: str = Field(alias="Val")
    enum: list[str] = Field(alias="Enum")


class WattsTargetValue(BaseModel):
    """Snowmelt target sub-field (e.g. Slab, MeltTime)."""

    model_config = ConfigDict(extra="ignore")

    val: float | int | None = Field(None, alias="Val")
    status: str | None = Field(None, alias="Status")


class WattsTarget(BaseModel):
    """Setpoints — thermostats use Heat/Cool; snowmelt uses Slab/MeltTime."""

    model_config = ConfigDict(extra="ignore")

    heat: float | None = Field(None, alias="Heat")
    cool: float | None = Field(None, alias="Cool")
    min: float | None = Field(None, alias="Min")
    max: float | None = Field(None, alias="Max")
    steps: float | None = Field(None, alias="Steps")
    slab: WattsTargetValue | None = Field(None, alias="Slab")
    melt_time: WattsTargetValue | None = Field(None, alias="MeltTime")


class WattsTempUnits(BaseModel):
    model_config = ConfigDict(extra="ignore")

    val: str = Field(alias="Val")


class WattsFan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    val: str = Field(alias="Val")
    enum: list[str] = Field(alias="Enum")


class WattsSchedEnable(BaseModel):
    model_config = ConfigDict(extra="ignore")

    val: str = Field(alias="Val")


class WattsNumericSetting(BaseModel):
    """Numeric configuration or setpoint with optional range."""

    model_config = ConfigDict(extra="ignore")

    active: int | None = Field(None, alias="Active")
    val: float | int | None = Field(None, alias="Val")
    min: float | None = Field(None, alias="Min")
    max: float | None = Field(None, alias="Max")
    steps: float | None = Field(None, alias="Steps")


class WattsEnumSetting(BaseModel):
    """Enum configuration such as MeltMan Stop/Melt or Sensitivity levels."""

    model_config = ConfigDict(extra="ignore")

    active: int | None = Field(None, alias="Active")
    val: str | None = Field(None, alias="Val")
    enum: list[str] | None = Field(None, alias="Enum")


class WattsDeviceData(BaseModel):
    """Runtime device state. Fields present depend on device kind."""

    model_config = ConfigDict(extra="ignore")

    sensors: WattsSensors | None = Field(None, alias="Sensors")
    state: WattsState | None = Field(None, alias="State")
    mode: WattsMode | None = Field(None, alias="Mode")
    target: WattsTarget | None = Field(None, alias="Target")
    temp_units: WattsTempUnits | None = Field(None, alias="TempUnits")
    sched_enable: WattsSchedEnable | None = Field(None, alias="SchedEnable")
    fan: WattsFan | None = Field(None, alias="Fan")
    melt: WattsNumericSetting | None = Field(None, alias="Melt")
    melt_man: WattsEnumSetting | None = Field(None, alias="MeltMan")
    melt_man_time: WattsNumericSetting | None = Field(None, alias="MeltManTime")
    melt_add_time: WattsNumericSetting | None = Field(None, alias="MeltAddTime")
    idle_enable: WattsEnumSetting | None = Field(None, alias="IdleEnable")
    idle: WattsNumericSetting | None = Field(None, alias="Idle")
    storm_enable: WattsEnumSetting | None = Field(None, alias="StormEnable")
    storm: WattsNumericSetting | None = Field(None, alias="Storm")
    storm_run_time: WattsNumericSetting | None = Field(None, alias="StormRunTime")
    wwsd_enable: WattsEnumSetting | None = Field(None, alias="WWSDEnable")
    wwsd: WattsNumericSetting | None = Field(None, alias="WWSD")
    cwco_enable: WattsEnumSetting | None = Field(None, alias="CWCOEnable")
    cwco: WattsNumericSetting | None = Field(None, alias="CWCO")
    sensitivity: WattsEnumSetting | None = Field(None, alias="Sensitivity")


class WattsDevice(BaseModel):
    """Top-level device from GET /Location/{id}/Devices."""

    model_config = ConfigDict(extra="ignore")

    device_id: str = Field(alias="deviceId")
    name: str
    model_number: str = Field(alias="modelNumber")
    model_id: int | None = Field(None, alias="modelId")
    device_type: str | None = Field(None, alias="deviceType")
    device_type_id: int | None = Field(None, alias="deviceTypeId")
    is_connected: bool = Field(alias="isConnected")
    data: WattsDeviceData | None = None

    @property
    def kind(self) -> WattsDeviceKind:
        """Return the device category, preferring API deviceType over model number."""
        if (
            self.device_type == DEVICE_TYPE_SNOWMELT
            or self.model_number in SNOWMELT_MODEL_NUMBERS
        ):
            return WattsDeviceKind.SNOWMELT
        if (
            self.device_type == DEVICE_TYPE_THERMOSTAT
            or self.model_number in THERMOSTAT_MODEL_NUMBERS
        ):
            return WattsDeviceKind.THERMOSTAT
        return WattsDeviceKind.UNKNOWN

    @property
    def is_thermostat(self) -> bool:
        return self.kind == WattsDeviceKind.THERMOSTAT

    @property
    def is_snowmelt(self) -> bool:
        return self.kind == WattsDeviceKind.SNOWMELT
