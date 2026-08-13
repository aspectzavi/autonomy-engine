from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BrowserConfigSection(BaseModel):
    """
    Base class for nested browser configuration models.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )