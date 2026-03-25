from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SshKey(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    pub_key: str
    is_active: bool


class CreateSshKey(BaseModel):
    name: str
    pub_key: str
    is_active: bool = True


class UpdateSshKey(BaseModel):
    name: str
    is_active: bool
