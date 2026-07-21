from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class DateRange(BaseModel):
    start: date
    end: date

class UploadResponse(BaseModel):
    session_id: str
    bank_name: str
    transaction_count: int
    date_range: DateRange
    status: str

class Summary(BaseModel):
    total_income: float
    total_expense: float
    net_savings: float
    savings_rate: float
    avg_daily_spend: float
    salary: float

class CategoryBreakdownItem(BaseModel):
    category: str
    amount: float
    count: int
    percentage: float

class AvoidableSplit(BaseModel):
    avoidable: float
    unavoidable: float

class DailySpending(BaseModel):
    date: str
    amount: float

class Insight(BaseModel):
    emoji: str
    text: str

class DayWiseSpend(BaseModel):
    day: str
    average_amount: float

class AnalyticsResponse(BaseModel):
    summary: Summary
    category_breakdown: List[CategoryBreakdownItem]
    avoidable_split: AvoidableSplit
    daily_spending: List[DailySpending]
    day_wise_spend: List[DayWiseSpend]
    insights: List[Insight]

class TransactionResponse(BaseModel):
    id: int
    date: date
    description: str
    amount: float
    type: str
    balance: Optional[float] = None
    category: Optional[str] = None
    category_confidence: Optional[float] = None
    categorization_method: Optional[str] = None
    is_avoidable: bool
    is_user_overridden: bool
    is_salary: bool

class TransactionUpdateRequest(BaseModel):
    is_avoidable: bool
