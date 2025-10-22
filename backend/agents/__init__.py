# This file makes the agents directory a Python package

from .simple_chat import simple_chat_agent
from .analytics_agent import (
    generate_sales_forecast,
    generate_customer_insights,
    generate_menu_optimization,
    generate_marketing_insights,
    detect_anomalies,
    generate_comprehensive_analytics_report
)

__all__ = [
    "simple_chat_agent",
    "generate_sales_forecast",
    "generate_customer_insights",
    "generate_menu_optimization",
    "generate_marketing_insights",
    "detect_anomalies",
    "generate_comprehensive_analytics_report"
]