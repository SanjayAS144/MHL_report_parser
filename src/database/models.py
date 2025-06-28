"""SQLAlchemy database models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# Enums
class SourceType(enum.Enum):
    PLATFORM = "platform"
    MANAGEMENT_SYSTEM = "management_system"


class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderType(enum.Enum):
    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"


class DeliveryType(enum.Enum):
    PLATFORM = "platform"
    SELF = "self"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    WALLET = "wallet"
    NET_BANKING = "net_banking"


class SponsorType(enum.Enum):
    PARTNER = "partner"
    OUTLET = "outlet"
    BRAND = "brand"
    CHAIN = "chain"


class CampaignType(enum.Enum):
    DISCOUNT = "discount"
    CASHBACK = "cashback"
    PROMOTIONAL = "promotional"


class CampaignStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


# Platform Management Schema
class RestaurantChain(Base):
    __tablename__ = 'restaurant_chains'
    
    chain_id = Column(String(50), primary_key=True)
    chain_name = Column(String(255), nullable=False)
    chain_description = Column(Text)
    headquarters_location = Column(String(255))
    website_url = Column(String(500))
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    brands = relationship("Brand", back_populates="chain")


class Brand(Base):
    __tablename__ = 'brands'
    
    brand_id = Column(String(50), primary_key=True)
    chain_id = Column(String(50), ForeignKey('restaurant_chains.chain_id'), nullable=False)
    brand_name = Column(String(255), nullable=False)
    brand_description = Column(Text)
    cuisine_type = Column(String(100))
    price_range = Column(String(20))
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    chain = relationship("RestaurantChain", back_populates="brands")
    outlets = relationship("Outlet", back_populates="brand")


class Outlet(Base):
    __tablename__ = 'outlets'
    
    outlet_id = Column(String(50), primary_key=True)
    brand_id = Column(String(50), ForeignKey('brands.brand_id'), nullable=False)
    outlet_name = Column(String(255), nullable=False)
    outlet_address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    country = Column(String(100), default='India')
    postal_code = Column(String(20))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    phone_number = Column(String(20))
    email = Column(String(255))
    manager_name = Column(String(255))
    opening_hours = Column(Text)
    seating_capacity = Column(Integer)
    has_delivery = Column(Boolean, default=True)
    has_dine_in = Column(Boolean, default=True)
    has_takeaway = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    brand = relationship("Brand", back_populates="outlets")
    partner_outlets = relationship("PartnerOutlet", back_populates="outlet")


class Partner(Base):
    __tablename__ = 'partners'
    
    partner_id = Column(String(50), primary_key=True)
    partner_name = Column(String(255), nullable=False)
    partner_type = Column(String(50))
    commission_rate = Column(Numeric(5, 4))
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    api_endpoint = Column(String(500))
    webhook_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    partner_outlets = relationship("PartnerOutlet", back_populates="partner")


class PartnerOutlet(Base):
    __tablename__ = 'partner_outlets'
    
    partner_outlet_id = Column(String(50), primary_key=True)
    partner_id = Column(String(50), ForeignKey('partners.partner_id'), nullable=False)
    outlet_id = Column(String(50), ForeignKey('outlets.outlet_id'), nullable=False)
    partner_outlet_name = Column(String(255))
    partner_outlet_code = Column(String(100))
    commission_rate = Column(Numeric(5, 4))
    is_active = Column(Boolean, default=True)
    onboarding_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('partner_id', 'outlet_id'),)
    
    partner = relationship("Partner", back_populates="partner_outlets")
    outlet = relationship("Outlet", back_populates="partner_outlets")


class OrderSource(Base):
    __tablename__ = 'order_sources'
    
    source_id = Column(String(50), primary_key=True)
    source_name = Column(String(255), nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Transaction Processing Schema
class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(String(50), primary_key=True)
    customer_name = Column(String(255))
    email = Column(String(255))
    phone_number = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default='India')
    postal_code = Column(String(20))
    date_of_birth = Column(DateTime)
    registration_date = Column(DateTime)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(String(50), primary_key=True)
    partner_outlet_id = Column(String(50), ForeignKey('partner_outlets.partner_outlet_id'), nullable=False)
    source_id = Column(String(50), ForeignKey('order_sources.source_id'), nullable=False)
    customer_id = Column(String(50), ForeignKey('customers.customer_id'))
    order_date = Column(DateTime, nullable=False)
    order_status = Column(Enum(OrderStatus), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    delivery_type = Column(Enum(DeliveryType))
    delivery_address = Column(Text)
    delivery_instructions = Column(Text)
    estimated_delivery_time = Column(DateTime)
    actual_delivery_time = Column(DateTime)
    table_number = Column(String(20))
    customer_name = Column(String(255))
    customer_phone = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    order_items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'
    
    order_item_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False)
    item_name = Column(String(255), nullable=False)
    item_description = Column(Text)
    category = Column(String(100))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    special_instructions = Column(Text)
    is_customization = Column(Boolean, default=False)
    parent_item_id = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    
    order = relationship("Order", back_populates="order_items")


class Payment(Base):
    __tablename__ = 'payments'
    
    payment_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='INR')
    transaction_id = Column(String(255))
    payment_gateway = Column(String(100))
    payment_date = Column(DateTime)
    processed_date = Column(DateTime)
    failure_reason = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    order = relationship("Order", back_populates="payments")


class DiscountsApplied(Base):
    __tablename__ = 'discounts_applied'
    
    discount_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False)
    discount_name = Column(String(255), nullable=False)
    discount_code = Column(String(100))
    discount_type = Column(String(50))
    discount_amount = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2))
    sponsor_type = Column(Enum(SponsorType))
    sponsor_entity_id = Column(String(50))
    sponsor_share_percentage = Column(Numeric(5, 2))
    sponsor_share_amount = Column(Numeric(10, 2))
    applied_at = Column(DateTime, default=func.now())


class OrderFinancialDetail(Base):
    __tablename__ = 'order_financial_details'
    
    financial_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    delivery_charges = Column(Numeric(10, 2), default=0)
    service_charges = Column(Numeric(10, 2), default=0)
    packaging_charges = Column(Numeric(10, 2), default=0)
    total_discounts = Column(Numeric(10, 2), default=0)
    final_amount = Column(Numeric(10, 2), nullable=False)
    commission_amount = Column(Numeric(10, 2))
    commission_rate = Column(Numeric(5, 4))
    settlement_amount = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Customer Experience Schema
class CustomerFeedback(Base):
    __tablename__ = 'customer_feedback'
    
    feedback_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'))
    customer_id = Column(String(50), ForeignKey('customers.customer_id'))
    outlet_id = Column(String(50), ForeignKey('outlets.outlet_id'))
    overall_rating = Column(Integer)
    food_rating = Column(Integer)
    service_rating = Column(Integer)
    delivery_rating = Column(Integer)
    comments = Column(Text)
    feedback_date = Column(DateTime, default=func.now())
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class MarketingCampaign(Base):
    __tablename__ = 'marketing_campaigns'
    
    campaign_id = Column(String(50), primary_key=True)
    campaign_name = Column(String(255), nullable=False)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    target_audience = Column(String(255))
    budget = Column(Numeric(12, 2))
    discount_percentage = Column(Numeric(5, 2))
    discount_amount = Column(Numeric(10, 2))
    min_order_amount = Column(Numeric(10, 2))
    max_discount_amount = Column(Numeric(10, 2))
    usage_limit = Column(Integer)
    current_usage = Column(Integer, default=0)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.ACTIVE)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Analytics Reporting Schema
class SettlementReport(Base):
    __tablename__ = 'settlement_reports'
    
    settlement_id = Column(String(50), primary_key=True)
    partner_id = Column(String(50), ForeignKey('partners.partner_id'), nullable=False)
    outlet_id = Column(String(50), ForeignKey('outlets.outlet_id'), nullable=False)
    settlement_date = Column(DateTime, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    total_orders = Column(Integer, default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    commission_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    adjustment_amount = Column(Numeric(12, 2), default=0)
    settlement_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DailyMetric(Base):
    __tablename__ = 'daily_metrics'
    
    metric_id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    outlet_id = Column(String(50), ForeignKey('outlets.outlet_id'), nullable=False)
    partner_id = Column(String(50), ForeignKey('partners.partner_id'))
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Numeric(12, 2), default=0)
    total_commission = Column(Numeric(12, 2), default=0)
    average_order_value = Column(Numeric(10, 2), default=0)
    customer_count = Column(Integer, default=0)
    new_customers = Column(Integer, default=0)
    repeat_customers = Column(Integer, default=0)
    cancellation_rate = Column(Numeric(5, 2), default=0)
    delivery_time_avg = Column(Integer)
    rating_average = Column(Numeric(3, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (UniqueConstraint('date', 'outlet_id', 'partner_id'),)


class Invoice(Base):
    __tablename__ = 'invoices'
    
    invoice_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False)
    invoice_number = Column(String(100), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default='generated')
    payment_terms = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class OrderReconciliation(Base):
    __tablename__ = 'order_reconciliation'
    
    reconciliation_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.order_id'), nullable=False)
    partner_id = Column(String(50), ForeignKey('partners.partner_id'), nullable=False)
    reconciliation_date = Column(DateTime, nullable=False)
    system_amount = Column(Numeric(10, 2), nullable=False)
    partner_amount = Column(Numeric(10, 2), nullable=False)
    variance_amount = Column(Numeric(10, 2), default=0)
    variance_reason = Column(Text)
    status = Column(String(50), default='pending')
    resolved_by = Column(String(100))
    resolved_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 