"""Constants for the Watts Home (Tekmar) integration."""

from typing import Final

DOMAIN: Final = "watts_home"

CLIENT_ID: Final = "4b3a6465-94dd-47c2-976c-18bc29c53c2f"
API_BASE_URL: Final = "https://home.watts.com/api"
AUTH_HOST: Final = "https://login.watts.io"
TENANT: Final = "wattsb2cap02.onmicrosoft.com"
POLICY: Final = "B2C_1A_Residential_UnifiedSignUpOrSignIn"
SCOPE: Final = "https://wattsb2cap02.onmicrosoft.com/wattsapiresi/manage offline_access openid profile"
REDIRECT_URI: Final = f"msal{CLIENT_ID}://auth"
BROWSER_UA: Final = (
    "Dalvik/2.1.0 (Linux; U; Android 16; SM-S901W Build/BP2A.250605.031.A3)"
)
CODE_VERIFIER: Final = "DM6nhvQSKnj72gkQQ5T1tCgCYGy5vdXnzdIQw3Bh46TX7pDvAcisyWDyt5UL3NQH8q4NoqMvRICQRmxCeDU3qHj8Jvciqo4RHcRiyjIlbB9q0k8LnUu8zHIdJHRLtk3J"

DEFAULT_SCAN_INTERVAL: Final = 60
MIN_SCAN_INTERVAL: Final = 30
MAX_SCAN_INTERVAL: Final = 3600

CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_SCAN_INTERVAL: Final = "scan_interval"

TOKEN_REFRESH_BUFFER_SECONDS: Final = 120

DEVICE_TYPE_THERMOSTAT: Final = "Thermostat"
DEVICE_TYPE_SNOWMELT: Final = "SnowMelt"

THERMOSTAT_MODEL_NUMBERS: frozenset[str] = frozenset({"561", "562", "563", "564"})
SNOWMELT_MODEL_NUMBERS: frozenset[str] = frozenset({"670", "671"})

MODEL_NAMES: dict[str, str] = {
    "561": "Tekmar WiFi Thermostat 561",
    "562": "Tekmar WiFi Thermostat 562",
    "563": "Tekmar WiFi Thermostat 563",
    "564": "Tekmar WiFi Thermostat 564",
    "670": "Tekmar WiFi Snow Melting Control 670",
    "671": "Tekmar WiFi Snow Melting Control 671",
}


def device_model_name(model_number: str) -> str:
    """Return a human-readable model name for a device."""
    if model_number in MODEL_NAMES:
        return MODEL_NAMES[model_number]
    if model_number in SNOWMELT_MODEL_NUMBERS:
        return f"Tekmar WiFi Snow Melting Control {model_number}"
    return f"Tekmar WiFi Thermostat {model_number}"

# Maps Watts API HVAC mode values to Home Assistant HVAC modes.
# Keys match exactly what the API returns (title-case).
WATTS_TO_HA_MODE: dict[str, str] = {
    "Heat": "heat",
    "Cool": "cool",
    "Auto": "heat_cool",
    "Off": "off",
    "Fan": "fan_only",
    "Dry": "dry",
    "Dehumidify": "dry",
}

# Maps Home Assistant HVAC modes back to Watts API mode values (title-case).
HA_TO_WATTS_MODE: dict[str, str] = {
    "heat": "Heat",
    "cool": "Cool",
    "heat_cool": "Auto",
    "off": "Off",
    "fan_only": "Fan",
    "dry": "Dry",
}

# Maps Watts State.Op values to Home Assistant HVAC actions.
# Keys match exactly what the API returns (title-case).
WATTS_TO_HA_ACTION: dict[str, str] = {
    "Heat": "heating",
    "Cool": "cooling",
    "Off": "off",
    "": "idle",
}
