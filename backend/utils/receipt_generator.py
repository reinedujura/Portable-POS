"""Receipt generation utilities for multiple formats"""

from typing import Dict, List, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def generate_receipt_text(receipt_data: Dict) -> str:
    """
    Generate a formatted text receipt.
    
    Args:
        receipt_data: Dictionary containing receipt information
        
    Returns:
        Formatted text receipt as string
    """
    receipt = []
    receipt.append("=" * 50)
    receipt.append(f"        {receipt_data.get('business_name','').upper()}")
    receipt.append("=" * 50)
    receipt.append(f"Transaction ID: {receipt_data.get('transaction_id','')}")
    receipt.append(f"Date & Time: {receipt_data.get('date_time','')}")
    receipt.append(f"Customer: {receipt_data.get('customer_name') or 'Walk-in'}")
    receipt.append("-" * 50)

    # Items
    receipt.append("ITEMS:")
    for item in receipt_data.get('items', []):
        receipt.append(f"{item.get('quantity',1)}x {item.get('offering_name','')}")
        receipt.append(f"    @ MYR {float(item.get('unit_price',0)):.2f} = MYR {float(item.get('total_price',0)):.2f}")

    receipt.append("-" * 50)
    receipt.append(f"Subtotal:        MYR {receipt_data.get('subtotal',0):.2f}")

    if receipt_data.get('discount_amount', 0) > 0:
        receipt.append(f"Discount:       -MYR {receipt_data.get('discount_amount',0):.2f}")

    if receipt_data.get('tax_amount', 0) > 0:
        receipt.append(f"Tax/VAT:        +MYR {receipt_data.get('tax_amount',0):.2f}")

    receipt.append("=" * 50)
    receipt.append(f"TOTAL:           MYR {receipt_data.get('final_total',0):.2f}")
    receipt.append("=" * 50)

    receipt.append(f"Payment Method: {receipt_data.get('payment_method','')}")
    if receipt_data.get('amount_tendered'):
        receipt.append(f"Amount Tendered: MYR {receipt_data.get('amount_tendered',0):.2f}")
        receipt.append(f"Change Given:    MYR {receipt_data.get('change_given',0):.2f}")

    if receipt_data.get('notes'):
        receipt.append("-" * 50)
        receipt.append(f"Notes: {receipt_data.get('notes')}")

    receipt.append("-" * 50)
    receipt.append("Thank you for your business!")
    receipt.append("Please keep this receipt for your records.")
    receipt.append("=" * 50)

    return "\n".join(receipt)


def generate_receipt_csv(receipt_data: Dict) -> str:
    """
    Generate CSV format receipt data.
    
    Args:
        receipt_data: Dictionary containing receipt information
        
    Returns:
        CSV formatted receipt as string
    """
    csv_lines = []
    csv_lines.append("Field,Value")
    csv_lines.append(f"Business,{receipt_data['business_name']}")
    csv_lines.append(f"Transaction ID,{receipt_data['transaction_id']}")
    csv_lines.append(f"Date Time,{receipt_data['date_time']}")
    csv_lines.append(f"Customer,{receipt_data.get('customer_name', 'Walk-in')}")
    csv_lines.append(f"Items,{len(receipt_data.get('items', []))}")
    csv_lines.append(f"Subtotal,{receipt_data.get('subtotal', 0)}")
    csv_lines.append(f"Discount,{receipt_data.get('discount_amount', 0)}")
    csv_lines.append(f"Tax,{receipt_data.get('tax_amount', 0)}")
    csv_lines.append(f"Total,{receipt_data.get('final_total', 0)}")
    csv_lines.append(f"Payment Method,{receipt_data.get('payment_method', '')}")
    csv_lines.append(f"Amount Tendered,{receipt_data.get('amount_tendered', 0)}")
    csv_lines.append(f"Change Given,{receipt_data.get('change_given', 0)}")
    if receipt_data.get('notes'):
        csv_lines.append(f"Notes,{receipt_data.get('notes')}")
    
    return "\n".join(csv_lines)


def extract_payment_method(notes: str) -> str:
    """
    Extract payment method from transaction notes.
    
    Args:
        notes: Transaction notes string
        
    Returns:
        Extracted payment method or 'Unknown'
    """
    if not notes:
        return "Unknown"
    
    payment_keywords = {
        'cash': ['cash', 'paid cash', 'cash payment'],
        'card': ['card', 'credit', 'debit', 'visa', 'mastercard'],
        'check': ['check', 'cheque'],
        'mobile': ['mobile', 'e-wallet', 'tng', 'grab', 'gcash', 'dana'],
        'bank': ['bank', 'transfer', 'fpx', 'online']
    }
    
    notes_lower = notes.lower()
    for method, keywords in payment_keywords.items():
        if any(keyword in notes_lower for keyword in keywords):
            return method.capitalize()
    
    return "Unknown"


def format_currency(amount: float, currency: str = "MYR") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Numeric amount
        currency: Currency code (default: MYR)
        
    Returns:
        Formatted currency string
    """
    return f"{currency} {float(amount):.2f}"
