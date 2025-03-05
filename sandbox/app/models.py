from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Payer(Base):
    __tablename__ = "payers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    mrf_index_file_url = Column(String)


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    payer_id = Column(Integer, ForeignKey("payers.id"))
    name = Column(String, nullable=False)
    type = Column(String)
    plan_market_type = Column(String)
    category_id = Column(String)
    category_id_type = Column(String)

    payer = relationship("Payer", backref="plans")


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True)
    npi = Column(String, unique=True, nullable=False)


class ProviderGroup(Base):
    __tablename__ = "provider_groups"

    id = Column(Integer, primary_key=True)
    payer_id = Column(Integer, ForeignKey("payers.id"))
    payer_assigned_id = Column(String, unique=True, nullable=False)  # Maps to provider_group_id in JSON
    ein = Column(String)

    payer = relationship("Payer", backref="provider_groups")


class ProviderGroupMember(Base):
    __tablename__ = "provider_group_members"

    provider_group_id = Column(Integer, ForeignKey("provider_groups.id"), primary_key=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), primary_key=True)

    provider_group = relationship("ProviderGroup", backref="members")
    provider = relationship("Provider", backref="groups")


class FeeSchedule(Base):
    __tablename__ = "fee_schedules"

    id = Column(Integer, primary_key=True)
    payer_id = Column(Integer, ForeignKey("payers.id"))
    description = Column(String, nullable=False)
    source_file_url = Column(String)

    payer = relationship("Payer", backref="fee_schedules")


class PlanFeeSchedule(Base):
    __tablename__ = "plan_fee_schedules"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    fee_schedule_id = Column(Integer, ForeignKey("fee_schedules.id"))

    plan = relationship("Plan", backref="fee_schedules")
    fee_schedule = relationship("FeeSchedule", backref="plans")


class ServiceLine(Base):
    __tablename__ = "service_lines"

    id = Column(Integer, primary_key=True)
    billing_code = Column(String, nullable=False)
    billing_code_type = Column(String, nullable=False)
    billing_code_type_version = Column(String)


class NegotiatedRate(Base):
    __tablename__ = "negotiated_rates"

    id = Column(Integer, primary_key=True)
    payer_id = Column(Integer, ForeignKey("payers.id"))
    fee_schedule_id = Column(Integer, ForeignKey("fee_schedules.id"))
    service_line_id = Column(Integer, ForeignKey("service_lines.id"))
    negotiation_arrangement = Column(String, nullable=False)
    negotiated_type = Column(String, nullable=False)
    negotiated_rate = Column(Numeric(10, 2), nullable=False)
    expiration_date = Column(Date)
    billing_class = Column(String, nullable=False)
    service_codes = Column(ARRAY(Text))  # Storing service codes as an array of strings

    payer = relationship("Payer", backref="negotiated_rates")
    fee_schedule = relationship("FeeSchedule", backref="negotiated_rates")
    service_line = relationship("ServiceLine", backref="negotiated_rates")


class NegotiatedRateProviderGroup(Base):
    __tablename__ = "negotiated_rate_provider_groups"

    id = Column(Integer, primary_key=True)
    negotiated_rate_id = Column(Integer, ForeignKey("negotiated_rates.id"))
    provider_group_id = Column(Integer, ForeignKey("provider_groups.id"))

    negotiated_rate = relationship("NegotiatedRate", backref="provider_groups")
    provider_group = relationship("ProviderGroup", backref="negotiated_rates")
