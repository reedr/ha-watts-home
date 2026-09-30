"""Pydantic v2 models for Watts Home API device responses."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .const import (
    DEVICE_TYPE_SETPOINT,
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
    """Sensor group — thermostats use Room/Floor/Outdoor/RH; snowmelt adds Slab/Water.

    Setpoint controls report numbered inputs (Sensor1, ...) instead of Room.
    """

    model_config = ConfigDict(extra="allow")

    room: WattsSensor | None = Field(None, alias="Room")
    floor: WattsSensor | None = Field(None, alias="Floor")
    outdoor: WattsSensor | None = Field(None, alias="Outdoor")
    rh: WattsSensor | None = Field(None, alias="RH")
    slab: WattsSensor | None = Field(None, alias="Slab")
    water: WattsSensor | None = Field(None, alias="Water")

    def by_name(self, name: str) -> WattsSensor | None:
        """Look up a sensor by the name the API uses for it."""
        declared = {
            "room": self.room,
            "floor": self.floor,
            "outdoor": self.outdoor,
            "rh": self.rh,
        }
        if (sensor := declared.get(name.lower())) is not None:
            return sensor
        raw = (self.model_extra or {}).get(name)
        if isinstance(raw, dict):
            try:
                return WattsSensor.model_validate(raw)
            except ValidationError:
                return None
        return None


class WattsState(BaseModel):
    """Operational state. Thermostats use Op=Heat/Cool/Off; snowmelt uses Sub for reason."""

    model_config = ConfigDict(extra="ignore")

    op: str = Field(alias="Op")
    sub: str = Field("None", alias="Sub")


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

    sensor: str | None = Field(None, alias="Sensor")
    heat: float | None = Field(None, alias="Heat")
    cool: float | None = Field(None, alias="Cool")
    min: float | None = Field(None, alias="Min")
    max: float | None = Field(None, alias="Max")
    steps: float | None = Field(None, alias="Steps")
    heat_min_limit: float | None = Field(None, alias="HeatMinLimit")
    heat_max_limit: float | None = Field(None, alias="HeatMaxLimit")
    cool_min_limit: float | None = Field(None, alias="CoolMinLimit")
    cool_max_limit: float | None = Field(None, alias="CoolMaxLimit")
    slab: WattsTargetValue | None = Field(None, alias="Slab")
    melt_time: WattsTargetValue | None = Field(None, alias="MeltTime")


class WattsTempUnits(BaseModel):
    model_config = ConfigDict(extra="ignore")

    val: str = Field(alias="Val")


class WattsFan(BaseModel):
    model_config = ConfigDict(extra="ignore")

    active: int = Field(0, alias="Active")
    val: str = Field(alias="Val")
    enum: list[str] = Field(alias="Enum")
    relay: int = Field(0, alias="Relay")


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


class WattsHumControl(BaseModel):
    active: int = Field(0, alias="Active")
    val: float = Field(alias="Val")
    min: float = Field(alias="Min")
    max: float = Field(alias="Max")
    steps: float = Field(alias="Steps")


class WattsFloorSetpoint(BaseModel):
    w: float = Field(0, alias="W")
    a: float = Field(0, alias="A")


class WattsSchedule(BaseModel):
    sched_active: int = Field(0, alias="SchedActive")
    heat_active: int = Field(0, alias="HeatActive")
    cool_active: int = Field(0, alias="CoolActive")
    floor_active: int = Field(0, alias="FloorActive")
    floor: WattsFloorSetpoint | None = Field(None, alias="Floor")
    floor_min: float = Field(0, alias="FloorMin")
    floor_max: float = Field(0, alias="FloorMax")
    heat_min: float | None = Field(None, alias="HeatMin")
    heat_max: float | None = Field(None, alias="HeatMax")
    cool_min: float | None = Field(None, alias="CoolMin")
    cool_max: float | None = Field(None, alias="CoolMax")


class WattsEnergyChannel(BaseModel):
    daily: list[float] = Field(default_factory=list, alias="Daily")
    monthly: list[float] = Field(default_factory=list, alias="Monthly")


class WattsEnergy(BaseModel):
    heat: WattsEnergyChannel | None = Field(None, alias="Heat")
    cool: WattsEnergyChannel | None = Field(None, alias="Cool")


class WattsLocation(BaseModel):
    location_id: str = Field(alias="locationId")
    name: str = ""
    away_state: int = Field(0, alias="awayState")
    user_type: int = Field(0, alias="userType")


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
    hum: WattsHumControl | None = Field(None, alias="Hum")
    dehum: WattsHumControl | None = Field(None, alias="Dehum")
    schedule: WattsSchedule | None = Field(None, alias="Schedule")
    energy: WattsEnergy | None = Field(None, alias="Energy")
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
    location: WattsLocation | None = None

    @property
    def kind(self) -> WattsDeviceKind:
        """Return the device category, preferring API deviceType over model number."""
        if (
            self.device_type == DEVICE_TYPE_SNOWMELT
            or self.model_number in SNOWMELT_MODEL_NUMBERS
        ):
            return WattsDeviceKind.SNOWMELT
        if (
            self.device_type in (DEVICE_TYPE_THERMOSTAT, DEVICE_TYPE_SETPOINT)
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
