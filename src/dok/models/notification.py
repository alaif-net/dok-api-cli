from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationEndpoint(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    created_at: str
    updated_at: str
    endpoint_type: str
    address: str
    is_verified: bool


class CreateNotificationEndpointRequest(BaseModel):
    endpoint_type: str
    address: str


class UpdateNotificationEndpointRequest(BaseModel):
    endpoint_type: Optional[str] = None
    address: Optional[str] = None


class NotificationSetting(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    created_at: str
    updated_at: str
    event_type: str
    is_enabled: bool
    endpoints: list[NotificationEndpoint]


class CreateNotificationSettingRequest(BaseModel):
    event_type: str
    is_enabled: bool
    endpoint_ids: list[str]


class UpdateNotificationSettingRequest(BaseModel):
    event_type: str
    is_enabled: bool
    endpoint_ids: list[str]


class PartialUpdateNotificationSettingRequest(BaseModel):
    event_type: Optional[str] = None
    is_enabled: Optional[bool] = None
    endpoint_ids: Optional[list[str]] = None


class TaskNotificationPreferenceRequest(BaseModel):
    is_enabled: Optional[bool] = None
    endpoint_ids: Optional[list[str]] = None


class TestWebhookRequest(BaseModel):
    url: str


class TestWebhookResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    ok: Optional[bool] = None
    webhook_status_code: Optional[int] = None
    response_body: Optional[str] = None
