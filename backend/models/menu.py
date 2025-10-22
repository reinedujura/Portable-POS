# models/menu.py - Data structures for products and services ("menu items")

from pydantic import BaseModel, Field  # Data validation framework
from typing import Optional  # For fields that can be None
from decimal import Decimal  # For precise money calculations

# Categories of things businesses can sell
MENU_CATEGORIES = [
    "main_dishes",     # Rice dishes, noodles, main meals
    "side_dishes",     # Vegetables, proteins, accompaniments  
    "beverages",       # Hot drinks, cold drinks, juices
    "desserts",        # Sweet treats, ice cream, local desserts
    "snacks",          # Light bites, finger foods
    "other"            # Anything else
]

class MenuItemCreateRequest(BaseModel):
    """What the user sends when adding a new menu item"""
    
    # Name of the product/service (e.g., "Nasi Lemak", "1-hour Math Tutoring")
    name: str = Field(
        ...,  # Required field
        min_length=1,  # Can't be empty
        max_length=100,  # Reasonable limit
        description="Name of your menu item or service"
    )
    
    # How much it costs (stored as string to avoid floating point issues)
    price: str = Field(
        ...,  # Required field
        pattern=r"^\d+(\.\d{1,2})?$",  # Must be valid money format (e.g., "12.50")
        description="Price in your base currency (e.g., '12.50')"
    )
    
    # What category this belongs to
    category: str = Field(
        ...,  # Required field
        description="Category of menu item"
    )
    
    # Optional: detailed description
    description: Optional[str] = Field(
        default=None,  # Not required
        max_length=500,  # Keep descriptions reasonable
        description="Detailed description (optional)"
    )
    
    # Optional: how many are available (None = unlimited)
    stock_quantity: Optional[int] = Field(
        default=None,  # Not required (unlimited stock)
        ge=0,  # Must be zero or positive
        description="Stock quantity (leave empty for unlimited)"
    )
    
    # Whether this is currently available for sale
    is_active: bool = Field(
        default=True,  # New menu items are active by default
        description="Whether this menu item is currently available"
    )
    
    class Config:
        json_schema_extra = {  # Example shown in API docs
            "example": {
                "name": "Nasi Lemak with Egg",
                "price": "8.50",
                "category": "food_drink",
                "description": "Traditional Malaysian breakfast with coconut rice, sambal, and fried egg",
                "stock_quantity": None,  # Unlimited
                "is_active": True
            }
        }

class MenuItemInDB(BaseModel):
    """How menu item data is stored in MongoDB"""
    
    id: str = Field(..., alias="_id", description="Unique menu item ID")  # MongoDB's _id field
    user_id: str  # Which business owns this menu item
    name: str  # Same as create request
    price: str  # Same as create request (stored as string)
    category: str  # Same as create request
    description: Optional[str] = None  # Same as create request
    stock_quantity: Optional[int] = None  # Same as create request
    is_active: bool  # Same as create request
    created_at: str  # Auto-generated timestamp
    updated_at: str  # Auto-generated timestamp
    
class MenuItemUpdateRequest(BaseModel):
    """What the user sends when updating an existing menu item"""
    
    # All fields are optional - user can update just what they want
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[str] = Field(None, pattern=r"^\d+(\.\d{1,2})?$")
    category: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None