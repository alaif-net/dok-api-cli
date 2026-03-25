from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ContainerRegistry(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    created_at: str
    updated_at: str
    hostname: str
    username: str


class CreateContainerRegistryRequest(BaseModel):
    hostname: str
    username: str
    password: str


class UpdateContainerRegistryRequest(BaseModel):
    hostname: str
    username: str
    password: str
