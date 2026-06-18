"""Tests for snowmelt API write helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from custom_components.watts_home.api import WattsApiClient


@pytest.mark.asyncio
async def test_set_setting_patch_payload() -> None:
    client = WattsApiClient(AsyncMock(), "token")
    with patch.object(client, "_patch", AsyncMock()) as mock_patch:
        await client.set_setting("device-1", "MeltMan", "Melt")
    mock_patch.assert_awaited_once_with(
        "/Device/device-1",
        {"Settings": {"MeltMan": "Melt"}},
    )
