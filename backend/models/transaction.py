# models/transaction.py - Data structures for sales transactions

from pydantic import BaseModel, Field  # Data validation framework
from typing import List, Optional  # For complex data types
from datetime import datetime  # For timestamps
from decimal import Decimal  # For precise money calculations

class TransactionItem(BaseModel):
    """A single item within a transaction (e.g., 2x Nasi Lemak)"""
    
    # Which offering was sold
    offering_id: str = Field(..., description="ID of the offering being sold")
    offering_name: str = Field(..., description="Name of offering (stored for history)")
    
    # Quantity and pricing
    quantity: int = Field(..., ge=1, description="How many of this item")
    unit_price: str = Field(..., description="Price per unit (stored as string)")
    total_price: str = Field(..., description="quantity × unit_price (stored as string)")

class TransactionCreateRequest(BaseModel):
    """What the user sends when recording a new sale"""
    
    # List of items being sold
    items: List[TransactionItem] = Field(
        ..., 
        min_items=1, 
        description="List of items being sold"
    )
    
    # Optional customer info (for receipts/records)
    customer_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Customer name (optional)"
    )
    
    # Optional notes about the transaction
    notes: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Transaction notes (optional)"
    )

class TransactionInDB(BaseModel):
    """How transaction data is stored in MongoDB"""
    
    id: str = Field(..., alias="_id", description="Unique transaction ID")
    user_id: str  # Which business recorded this sale
    
    # Transaction details
    items: List[TransactionItem]  # What was sold
    total_amount: str  # Total sale amount (sum of all item totals)
    currency: str  # Currency used (from user's base_currency)
    
    # Optional fields
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: str  # When the sale was recorded
    sale_date: str  # Date of the actual sale (might be different from created_at)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "60f1a1b2c3d4e5f6a7b8c9d0",
                "items": [
                    {
                        "offering_id": "60f1a1b2c3d4e5f6a7b8c9d1", 
                        "offering_name": "Nasi Lemak with Egg",
                        "quantity": 1,
                        "unit_price": "8.50",
                        "total_price": "8.50"
                    },
                    {
                        "offering_id": "60f1a1b2c3d4e5f6a7b8c9d2",
                        "offering_name": "Teh Tarik", 
                        "quantity": 2,
                        "unit_price": "3.00",
                        "total_price": "6.00"
                    }
                ],
                "total_amount": "14.50",
                "currency": "MYR",
                "customer_name": "Ahmad",
                "notes": "Extra spicy"
            }
        }