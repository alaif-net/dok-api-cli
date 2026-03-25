from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BillingDetail(BaseModel):
    model_config = ConfigDict(extra="allow")
    sequence_no: int
    plan: str
    usage_type: int
    usage: int
    amount: int
    description: str


class BillingInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    account: str
    bill_close_at: str
    details: list[BillingDetail]
    last_upload_at: str


class UnitPrice(BaseModel):
    model_config = ConfigDict(extra="allow")
    plan: str
    price: str
    is_overridden: bool
    begin_at: str
    end_at: str
