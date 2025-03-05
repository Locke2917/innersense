from pydantic import BaseModel, EmailStr
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# Payer Schemas
class PayerBase(BaseModel):
    name: str
    mrf_index_file_url: Optional[str] = None

class PayerCreate(PayerBase):
    pass

class PayerUpdate(PayerBase):
    pass

class PayerResponse(PayerBase):
    id: int
    class Config:
        from_attributes = True

# Plan Schemas
class PlanBase(BaseModel):
    payer_id: int
    name: str
    type: Optional[str] = None
    plan_market_type: Optional[str] = None
    category_id: Optional[str] = None
    category_id_type: Optional[str] = None

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id: int
    name: str
    type: Optional[str] = None
    plan_market_type: Optional[str] = None
    category_id: Optional[str] = None
    category_id_type: Optional[str] = None

    class Config:
        from_attributes = True

# Provider Schemas
class ProviderBase(BaseModel):
    npi: str

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(ProviderBase):
    pass

class ProviderResponse(ProviderBase):
    id: int
    class Config:
        from_attributes = True

# Provider Group Schemas
class ProviderGroupBase(BaseModel):
    payer_id: int
    payer_assigned_id: str
    ein: Optional[str] = None

class ProviderGroupCreate(ProviderGroupBase):
    pass

class ProviderGroupUpdate(ProviderGroupBase):
    pass

class ProviderGroupResponse(ProviderGroupBase):
    id: int
    class Config:
        from_attributes = True

# Fee Schedule Schemas
class FeeScheduleBase(BaseModel):
    payer_id: int
    description: str
    source_file_url: Optional[str] = None

class FeeScheduleCreate(FeeScheduleBase):
    pass

class FeeScheduleUpdate(FeeScheduleBase):
    pass

class FeeScheduleResponse(FeeScheduleBase):
    id: int
    class Config:
        from_attributes = True

# Plan Fee Schedule Schemas
class PlanFeeScheduleBase(BaseModel):
    plan_id: int
    fee_schedule_id: int

class PlanFeeScheduleCreate(PlanFeeScheduleBase):
    pass

class PlanFeeScheduleUpdate(PlanFeeScheduleBase):
    pass

class PlanFeeScheduleResponse(PlanFeeScheduleBase):
    id: int
    class Config:
        from_attributes = True

# Service Line Schemas
class ServiceLineBase(BaseModel):
    billing_code: str
    billing_code_type: str
    billing_code_type_version: str

class ServiceLineCreate(ServiceLineBase):
    pass

class ServiceLineUpdate(ServiceLineBase):
    pass

class ServiceLineResponse(ServiceLineBase):
    id: int
    class Config:
        from_attributes = True

# Negotiated Rate Schemas
class NegotiatedRateBase(BaseModel):
    payer_id: int
    fee_schedule_id: int
    service_line_id: int
    negotiation_arrangement: str
    negotiated_type: str
    negotiated_rate: float
    expiration_date: Optional[str] = None
    billing_class: str
    service_codes: List[str]

class NegotiatedRateCreate(NegotiatedRateBase):
    pass

class NegotiatedRateUpdate(NegotiatedRateBase):
    pass

class NegotiatedRateResponse(NegotiatedRateBase):
    id: int
    class Config:
        from_attributes = True

# Negotiated Rate Provider Group Schemas
class NegotiatedRateProviderGroupBase(BaseModel):
    negotiated_rate_id: int
    provider_group_id: int

class NegotiatedRateProviderGroupCreate(NegotiatedRateProviderGroupBase):
    pass

class NegotiatedRateProviderGroupUpdate(NegotiatedRateProviderGroupBase):
    pass

class NegotiatedRateProviderGroupResponse(NegotiatedRateProviderGroupBase):
    id: int
    class Config:
        from_attributes = True
