from datetime import date, datetime
from sqlalchemy import (
    String, Integer, Numeric, Boolean, Text, Date, DateTime,
    ForeignKey, UniqueConstraint, Index, Computed,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="units")
    lead_time_days: Mapped[int] = mapped_column(Integer, default=7)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inventory: Mapped["Inventory"] = relationship(back_populates="product", uselist=False)
    sales: Mapped[list["SalesHistory"]] = relationship(back_populates="product")
    forecasts: Mapped[list["DemandForecast"]] = relationship(back_populates="product")


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    avg_lead_time_days: Mapped[int] = mapped_column(Integer, default=7)
    reliability_score: Mapped[float] = mapped_column(Numeric(3, 2), default=0.90)
    price_rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0.50)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(back_populates="supplier")


class ProductSupplier(Base):
    __tablename__ = "product_suppliers"

    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.supplier_id", ondelete="CASCADE"), primary_key=True)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    min_order_qty: Mapped[int] = mapped_column(Integer, default=1)
    lead_time_days: Mapped[int | None] = mapped_column(Integer)


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), unique=True)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, default=50)
    reorder_qty: Mapped[int] = mapped_column(Integer, default=100)
    safety_stock: Mapped[int] = mapped_column(Integer, default=20)
    warehouse_location: Mapped[str | None] = mapped_column(String(50))
    last_restock_date: Mapped[date | None] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="inventory")


class SalesHistory(Base):
    __tablename__ = "sales_history"

    sale_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"))
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue: Mapped[float | None] = mapped_column(Numeric(12, 2))
    channel: Mapped[str] = mapped_column(String(50), default="in-store")
    promotion_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="sales")

    __table_args__ = (
        Index("idx_sales_product_date", "product_id", "sale_date"),
        Index("idx_sales_date", "sale_date"),
    )


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    po_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.supplier_id"))
    status: Mapped[str] = mapped_column(String(30), default="draft")
    total_amount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    order_date: Mapped[date] = mapped_column(Date, default=date.today)
    expected_delivery: Mapped[date | None] = mapped_column(Date)
    actual_delivery: Mapped[date | None] = mapped_column(Date)
    generated_by: Mapped[str] = mapped_column(String(50), default="agent")
    agent_reasoning: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")
    items: Mapped[list["PurchaseOrderItem"]] = relationship(back_populates="purchase_order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_po_status", "status"),
        Index("idx_po_supplier", "supplier_id"),
    )


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    po_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_orders.po_id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="items")


class RiskEvent(Base):
    __tablename__ = "risk_events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_suppliers: Mapped[str | None] = mapped_column(Text)
    affected_region: Mapped[str | None] = mapped_column(String(100))
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_risk_events_date", "event_date"),
        Index("idx_risk_events_severity", "severity"),
    )


class WeatherData(Base):
    __tablename__ = "weather_data"

    weather_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    temp_avg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    temp_min: Mapped[float | None] = mapped_column(Numeric(5, 2))
    temp_max: Mapped[float | None] = mapped_column(Numeric(5, 2))
    humidity: Mapped[float | None] = mapped_column(Numeric(5, 2))
    precipitation: Mapped[float | None] = mapped_column(Numeric(7, 2))
    weather_desc: Mapped[str | None] = mapped_column(String(100))
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("location", "record_date", name="uq_weather_location_date"),
    )


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    forecast_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"))
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)
    predicted_demand: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    lower_bound: Mapped[float | None] = mapped_column(Numeric(10, 2))
    upper_bound: Mapped[float | None] = mapped_column(Numeric(10, 2))
    model_version: Mapped[str] = mapped_column(String(50), default="prophet_v1")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="forecasts")

    __table_args__ = (
        UniqueConstraint("product_id", "forecast_date", "model_version", name="uq_forecast_product_date_model"),
        Index("idx_forecast_product_date", "product_id", "forecast_date"),
    )
