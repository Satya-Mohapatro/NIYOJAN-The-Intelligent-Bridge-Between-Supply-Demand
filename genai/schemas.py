from pydantic import BaseModel
from typing import Literal, Dict


class ForecastSummary(BaseModel):
    avg_daily_demand: float
    peak_demand: float
    trend: Literal["increasing", "decreasing", "stable"]


class InventoryStatus(BaseModel):
    current_stock: int
    days_of_cover: float
    reorder_threshold: int


class InsightInput(BaseModel):
    product_name: str
    forecast_summary: ForecastSummary
    inventory_status: InventoryStatus
    decision: Literal["RESTOCK", "HOLD", "REDUCE"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    context: Dict[str, str]


class LanguageInsight(BaseModel):
    summary: str
    risk: str
    action: str


class InsightOutput(BaseModel):
    english: LanguageInsight
    hindi: LanguageInsight
