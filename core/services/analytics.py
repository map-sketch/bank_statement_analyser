import json
import pandas as pd
from typing import List, Dict
from sqlalchemy.orm import Session
from core.models.db_models import TransactionModel, AnalyticsCacheModel
from core.models.schemas import AnalyticsResponse, Summary, CategoryBreakdownItem, AvoidableSplit, DailySpending, Insight, DayWiseSpend

# Categories deemed avoidable by default
AVOIDABLE_CATEGORIES = {"Food", "Entertainment", "Shopping", "Coffee", "Personal"}
UNAVOIDABLE_CATEGORIES = {"local commute", "Utilities", "Investments", "Rent", "EMI/Loans", "Grocery", "Travel", "Donation"}

def compute_analytics(db: Session, session_id: str):
    txns = db.query(TransactionModel).filter(TransactionModel.session_id == session_id).all()
    if not txns:
        return

    df = pd.DataFrame([{
        "id": t.id,
        "date": t.date,
        "description": t.description,
        "amount": t.amount,
        "type": t.type,
        "category": t.category,
        "is_avoidable": t.is_avoidable,
        "is_user_overridden": t.is_user_overridden
    } for t in txns])

    df["date"] = pd.to_datetime(df["date"])
    
    # 1. Salary Auto-Detection
    # Update is_salary flag
    for t in txns:
        if t.type == "CREDIT":
            if t.category == "Salary/Income":
                t.is_salary = True
            elif t.amount > 20000 and "salary" in str(t.description).lower():
                t.is_salary = True
    
    salary_amount = sum(t.amount for t in txns if t.is_salary)

    # 2. Avoidability Engine (if not user overridden)
    for t in txns:
        if not t.is_user_overridden:
            if t.category in AVOIDABLE_CATEGORIES:
                t.is_avoidable = True
            elif t.category in UNAVOIDABLE_CATEGORIES:
                t.is_avoidable = False
            else:
                t.is_avoidable = False # Default Others to False
                
    # Re-fetch after modifications to build summary
    # Calculate net category spending
    cat_net = {}
    for t in txns:
        if t.category not in cat_net:
            cat_net[t.category] = 0
        if t.type == "DEBIT":
            cat_net[t.category] += t.amount
        else:
            cat_net[t.category] -= t.amount

    total_expense = sum(amt for amt in cat_net.values() if amt > 0)
    total_income = sum(-amt for amt in cat_net.values() if amt < 0)

    avoidable_spend = sum(t.amount if t.type == "DEBIT" else -t.amount for t in txns if t.is_avoidable and cat_net[t.category] > 0)
    avoidable_spend = max(0, avoidable_spend)
    
    unavoidable_spend = sum(t.amount if t.type == "DEBIT" else -t.amount for t in txns if not t.is_avoidable and cat_net[t.category] > 0)
    unavoidable_spend = max(0, unavoidable_spend)
    
    # 3. Anomaly Filtering
    # Calculate avg daily spend excluding rent/emi/investments
    regular_spend = sum(t.amount if t.type == "DEBIT" else -t.amount for t in txns if cat_net[t.category] > 0 and t.category not in {"Rent", "EMI/Loans", "Investments"})
    
    dates = [t.date for t in txns]
    days = (max(dates) - min(dates)).days + 1 if dates else 1
    
    avg_daily_spend = regular_spend / days if days > 0 else 0
    
    # Flag anomalies (only for DEBITs)
    for t in txns:
        if t.type == "DEBIT" and t.category not in {"Rent", "EMI/Loans", "Investments"} and cat_net[t.category] > 0:
            if avg_daily_spend > 0 and t.amount > (avg_daily_spend * 3):
                t.is_anomaly = True

    # Compute daily spending (excluding anomalies, rent, and offsetting refunds)
    daily_totals = {}
    for t in txns:
        if not getattr(t, 'is_anomaly', False) and cat_net[t.category] > 0 and t.category != "Rent":
            d_str = t.date.strftime("%Y-%m-%d")
            amt = t.amount if t.type == "DEBIT" else -t.amount
            daily_totals[d_str] = daily_totals.get(d_str, 0) + amt
            
    daily_spending = [DailySpending(date=d, amount=max(0, amt)) for d, amt in sorted(daily_totals.items()) if amt > 0]

    # 4. Compute Day-wise Average Spends (per transaction)
    from collections import defaultdict
    day_spend_totals = defaultdict(list)
    for t in txns:
        if t.type == "DEBIT" and not getattr(t, 'is_anomaly', False):
            day_name = t.date.strftime("%A")
            day_spend_totals[day_name].append(t.amount)
            
    day_wise_spend = []
    days_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for day in days_order:
        amounts = day_spend_totals.get(day, [])
        avg_amt = sum(amounts) / len(amounts) if amounts else 0.0
        day_wise_spend.append(DayWiseSpend(day=day, average_amount=round(avg_amt, 2)))

    # 5. Generate Breakdown
    breakdown = []
    for cat, net_amt in cat_net.items():
        if net_amt > 0:
            count = sum(1 for t in txns if t.category == cat)
            percentage = (net_amt / total_expense * 100) if total_expense > 0 else 0
            breakdown.append(CategoryBreakdownItem(
                category=cat,
                amount=round(net_amt, 2),
                count=count,
                percentage=round(percentage, 2)
            ))

    # Insights Generation
    insights = []
    if total_expense > total_income:
        insights.append(Insight(emoji="🚨", text="You spent more than you earned this period."))
    
    savings = total_income - total_expense
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    if savings_rate > 20:
        insights.append(Insight(emoji="🌟", text=f"Great job! You saved {savings_rate:.1f}% of your income."))

    if avoidable_spend > (total_expense * 0.4):
        insights.append(Insight(emoji="🍔", text="High avoidable spending detected. Consider cutting back on dining and shopping."))

    # Generate Summary
    summary = Summary(
        total_income=total_income,
        total_expense=total_expense,
        net_savings=savings,
        savings_rate=round(savings_rate, 2),
        avg_daily_spend=round(avg_daily_spend, 2),
        salary=salary_amount
    )

    response = AnalyticsResponse(
        summary=summary,
        category_breakdown=breakdown,
        avoidable_split=AvoidableSplit(avoidable=avoidable_spend, unavoidable=unavoidable_spend),
        daily_spending=daily_spending,
        day_wise_spend=day_wise_spend,
        insights=insights
    )

    # Save to Cache
    cache = AnalyticsCacheModel(
        session_id=session_id,
        key="dashboard",
        value_json=response.model_dump_json()
    )
    db.add(cache)
    db.commit()
