from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlanID(str, Enum):
    v100_32gb = "v100-32gb"
    h100_80gb = "h100-80gb"
    h100_8gpu_80gb = "h100-8gpu-80gb"


class TaskStatus(str, Enum):
    waiting = "waiting"
    running = "running"
    error = "error"
    done = "done"
    aborted = "aborted"
    canceled = "canceled"


class ContainerSshShell(str, Enum):
    sh = "/bin/sh"
    bash = "/bin/bash"
    zsh = "/bin/zsh"


class ContainerSshDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")
    shell: ContainerSshShell
    port: int
    host_name: Optional[str] = None


class ContainerHttpDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")
    port: int
    path: str


class ContainerDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")
    image: str
    command: list[str]
    entrypoint: list[str]
    plan: PlanID
    registry: Optional[str] = None
    environment: Optional[dict[str, str]] = None
    ssh: Optional[ContainerSshDefinition] = None
    http: Optional[ContainerHttpDefinition] = None


class Container(BaseModel):
    model_config = ConfigDict(extra="allow")
    index: int
    image: str
    command: list[str]
    entrypoint: list[str]
    environment: dict[str, str]
    plan: PlanID
    registry: Optional[str] = None
    ssh: Optional[ContainerSshDefinition] = None
    http: Optional[ContainerHttpDefinition] = None
    exit_code: Optional[int] = None
    execution_seconds: Optional[int] = None
    start_at: Optional[str] = None
    stop_at: Optional[str] = None


class Artifact(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    task: str
    created_at: str
    deleted_at: Optional[str] = None
    filename: str
    size_bytes: int


class Task(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    created_at: str
    updated_at: str
    canceled_at: Optional[str] = None
    http_uri: Optional[str] = None
    containers: list[Container]
    status: TaskStatus
    tags: list[str]
    error_message: Optional[str] = None
    artifact: Optional[Artifact] = None
    execution_time_limit_sec: Optional[int] = None


class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    containers: list[ContainerDefinition]
    tags: list[str]
    execution_time_limit_sec: Optional[int] = None
