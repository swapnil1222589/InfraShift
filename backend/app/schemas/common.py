"""Common shared schema types."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class InfraShiftBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )


class PaginatedResponse(InfraShiftBaseModel):
    items: list[Any]
    total: int
    page: int = 1
    per_page: int = 50
