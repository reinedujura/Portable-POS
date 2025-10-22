#!/usr/bin/env python3
"""
AI Analytics Agent for POS System
Provides predictive analytics, sales forecasting, and smart recommendations
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from pymongo import MongoClient

# Initialize LLM for analytics
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), 
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
)


@tool
def fetch_sales_data(user_id: str, days: int = 30) -> str:
    """
    Fetch recent sales data from MongoDB for analysis.
    
    Args:
        user_id: The user/business ID
        days: Number of days to look back (default: 30)
    
    Returns:
        JSON string containing sales data for analysis
    """
    try:
        client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
        db = client["portable_pos_db"]
        transactions = db["transactions"]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch transactions
        query = {
            "user_id": user_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        sales = list(transactions.find(query).sort("created_at", -1))
        
        if sales:
            # Process sales data
            sales_summary = {
                "total_transactions": len(sales),
                "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "transactions": []
            }
            
            for sale in sales:
                sales_summary["transactions"].append({
                    "date": sale.get("sale_date", ""),
                    "amount": float(sale.get("total_amount", 0)),
                    "items_count": len(sale.get("items", [])),
                    "payment_method": sale.get("payment_method", ""),
                    "customer": sale.get("customer_name", "Walk-in")
                })
            
            return json.dumps(sales_summary)
        else:
            return json.dumps({"message": "No sales data found for the specified period"})
    except Exception as e:
        return json.dumps({"error": f"Error fetching sales data: {str(e)}"})
    finally:
        try:
            client.close()
        except:
            pass


@tool
def fetch_menu_items(user_id: str) -> str:
    """
    Fetch menu items and their sales performance.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        JSON string containing menu items and performance metrics
    """
    try:
        client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
        db = client["portable_pos_db"]
        menu = db["menu_items"]
        
        items = list(menu.find({"user_id": user_id}))
        
        if items:
            menu_summary = {
                "total_items": len(items),
                "items": []
            }
            
            for item in items:
                menu_summary["items"].append({
                    "name": item.get("offering_name", ""),
                    "category": item.get("category", ""),
                    "price": float(item.get("price") or item.get("unit_price", 0)),
                    "available": item.get("is_available", True)
                })
            
            return json.dumps(menu_summary)
        else:
            return json.dumps({"message": "No menu items found"})
    except Exception as e:
        return json.dumps({"error": f"Error fetching menu items: {str(e)}"})
    finally:
        try:
            client.close()
        except:
            pass


@tool
def fetch_customer_data(user_id: str) -> str:
    """
    Fetch customer data for behavior analysis and segmentation.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        JSON string containing customer statistics
    """
    try:
        client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
        db = client["portable_pos_db"]
        customers = db["customers"]
        
        customer_list = list(customers.find({"user_id": user_id}))
        
        if customer_list:
            customer_summary = {
                "total_customers": len(customer_list),
                "customers": []
            }
            
            for customer in customer_list:
                customer_summary["customers"].append({
                    "name": customer.get("name", ""),
                    "total_visits": customer.get("total_visits", 0),
                    "total_spent": float(customer.get("total_spent", 0)),
                    "avg_transaction": float(customer.get("total_spent", 0)) / max(customer.get("total_visits", 1), 1)
                })
            
            return json.dumps(customer_summary)
        else:
            return json.dumps({"message": "No customer data found"})
    except Exception as e:
        return json.dumps({"error": f"Error fetching customer data: {str(e)}"})
    finally:
        try:
            client.close()
        except:
            pass


def generate_sales_forecast(user_id: str) -> str:
    """
    Generate AI-powered sales forecast for the next 7-30 days.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        AI-generated forecast and insights
    """
    try:
        # Fetch sales data
        sales_data = fetch_sales_data.invoke({"user_id": user_id, "days": 90})
        menu_data = fetch_menu_items.invoke({"user_id": user_id})
        
        prompt = f"""You are a business analytics AI specializing in point-of-sale systems and sales forecasting.
        
Based on the following sales data:

{sales_data}

And menu information:

{menu_data}

Please provide:
1. **Sales Forecast** - Predict sales trends for the next 7, 14, and 30 days
2. **Seasonal Trends** - Identify any seasonal patterns or trends
3. **Demand Prediction** - Which products are likely to be most in demand
4. **Key Insights** - Notable patterns or anomalies in the data

Format your response with clear sections and actionable insights."""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating forecast: {str(e)}"


def generate_customer_insights(user_id: str) -> str:
    """
    Generate AI insights about customer behavior and segmentation.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        AI-generated customer insights
    """
    try:
        customer_data = fetch_customer_data.invoke({"user_id": user_id})
        sales_data = fetch_sales_data.invoke({"user_id": user_id, "days": 90})
        
        prompt = f"""You are a customer behavior analyst for a retail/service POS system.

Based on the following customer and sales data:

Customer Data:
{customer_data}

Sales Data:
{sales_data}

Please provide:
1. **Customer Segmentation** - Identify customer segments (high-value, frequent, at-risk, new)
2. **Churn Prediction** - Which customers might stop coming and why
3. **Behavioral Patterns** - How do customers typically behave?
4. **Retention Strategies** - Recommendations to improve customer loyalty

Format your response with clear, actionable insights."""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating customer insights: {str(e)}"


def generate_menu_optimization(user_id: str) -> str:
    """
    Generate AI recommendations for menu optimization and pricing.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        AI-generated menu optimization recommendations
    """
    try:
        menu_data = fetch_menu_items.invoke({"user_id": user_id})
        sales_data = fetch_sales_data.invoke({"user_id": user_id, "days": 90})
        
        prompt = f"""You are a menu optimization and pricing specialist for POS systems.

Based on the following menu and sales data:

Menu Data:
{menu_data}

Sales Data:
{sales_data}

Please provide:
1. **Menu Optimization** - Which items are underperforming and should be removed or repositioned?
2. **Pricing Recommendations** - Suggest price adjustments for items based on demand and margins
3. **Cross-Selling Opportunities** - Which items should be bundled or promoted together?
4. **New Item Suggestions** - What types of items should be added based on trends?

Format your response with specific, actionable recommendations."""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating menu optimization: {str(e)}"


def generate_marketing_insights(user_id: str) -> str:
    """
    Generate AI-powered marketing and promotion recommendations.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        AI-generated marketing insights
    """
    try:
        customer_data = fetch_customer_data.invoke({"user_id": user_id})
        sales_data = fetch_sales_data.invoke({"user_id": user_id, "days": 90})
        
        prompt = f"""You are a marketing strategist for small retail and service businesses.

Based on the following customer and sales data:

Customer Data:
{customer_data}

Sales Data:
{sales_data}

Please provide:
1. **Marketing Opportunities** - Identify key marketing angles and opportunities
2. **Promotion Strategies** - Suggest targeted promotions and campaigns
3. **Customer Engagement** - How to better engage customers and increase repeat visits?
4. **Best Times to Promote** - When should promotions run for maximum impact?
5. **Referral Potential** - Which customers are likely to refer others?

Format your response with practical, implementable marketing strategies."""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating marketing insights: {str(e)}"


def detect_anomalies(user_id: str) -> str:
    """
    Detect anomalies in sales patterns that might indicate issues.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        AI-identified anomalies and alerts
    """
    try:
        sales_data = fetch_sales_data.invoke({"user_id": user_id, "days": 60})
        
        prompt = f"""You are an anomaly detection specialist for POS systems.

Analyze the following sales data and identify any anomalies, unusual patterns, or alerts:

{sales_data}

Please provide:
1. **Anomalies Detected** - List any unusual patterns or suspicious activity
2. **Severity Assessment** - Rate the severity of each anomaly (Low/Medium/High)
3. **Possible Causes** - What might be causing these anomalies?
4. **Recommended Actions** - What should the business owner do about each anomaly?

Format your response with clear alerts and action items."""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error detecting anomalies: {str(e)}"


def generate_comprehensive_analytics_report(user_id: str) -> Dict[str, str]:
    """
    Generate a comprehensive analytics report covering all aspects.
    
    Args:
        user_id: The user/business ID
    
    Returns:
        Dictionary containing all analytics sections
    """
    return {
        "sales_forecast": generate_sales_forecast(user_id),
        "customer_insights": generate_customer_insights(user_id),
        "menu_optimization": generate_menu_optimization(user_id),
        "marketing_insights": generate_marketing_insights(user_id),
        "anomaly_detection": detect_anomalies(user_id),
        "generated_at": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🤖 AI Analytics Agent - Testing")
    print("=" * 50)
    
    # Example usage (would need a valid user_id from your system)
    test_user_id = "test_user_123"
    
    print("\n📊 Fetching sales data...")
    sales = fetch_sales_data.invoke({"user_id": test_user_id, "days": 30})
    print(f"Sales Data Sample: {sales[:200]}...")
    
    print("\n✅ Analytics Agent is ready for integration!")
