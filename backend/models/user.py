# models/user.py - Data structures for user registration and storage

from pydantic import BaseModel, Field  # Data validation framework
from typing import Optional  # For fields that can be None

# Only these 4 business types are allowed
BUSINESS_TYPES = ["street_vendor", "tutor", "yoga_teacher", "consultant"]


class UserRegisterRequest(BaseModel):
    """What the user sends when signing up"""
    
    business_name: str = Field(  # e.g., "Maria's Tacos"
        ...,  # Required field
        min_length=1,  # Can't be empty
        max_length=100,  # Reasonable limit
        description="Name of your business"
    )
    
    pin: str = Field(  # 4-digit login code (will be hashed)
        ...,  # Required field
        min_length=4,  # Must be exactly 4 chars
        max_length=4,  # Must be exactly 4 chars
        pattern=r"^\d{4}$",  # Only digits (0000-9999)
        description="4-digit PIN for login"
    )
    
    business_type: str = Field(  # One of: street_vendor, tutor, yoga_teacher, consultant
        ...,  # Required field
        description="Type of business"
    )
    
    base_currency: str = Field(  # ISO currency code (USD, EUR, MYR, etc.)
        default="MYR",  # Defaults to MYR (Malaysian Ringgit) if not provided
        max_length=3,  # Currency codes are always 3 letters
        description="Your base currency (e.g., MYR, USD, EUR)"
    )
    
    business_address: Optional[str] = Field(  # Optional: for legal receipts
        default=None,  # Not required
        max_length=200,  # Long enough for most addresses
        description="Business address (optional)"
    )
    
    tax_id: Optional[str] = Field(  # Optional: VAT/tax number
        default=None,  # Not required
        max_length=50,  # Flexible length
        description="Tax ID or VAT number (optional)"
    )
    
    class Config:
        json_schema_extra = {  # Example shown in API docs
            "example": {
                "business_name": "Nasi Lemak Siti",
                "pin": "1234",
                "business_type": "street_vendor",
                "base_currency": "MYR",
                "business_address": "Jalan Raja Laut, Kuala Lumpur",
                "tax_id": "C-1234567890"
            }
        }


class UserInDB(BaseModel):
    """How user data is stored in MongoDB (with extra fields we add)"""
    
    id: str = Field(..., alias="_id", description="Unique user ID")  # MongoDB's _id field
    business_name: str  # Same as registration
    pin_hash: str  # Hashed PIN (never store raw PIN!)
    business_type: str  # Same as registration
    base_currency: str  # Same as registration
    business_address: Optional[str] = None  # Same as registration
    tax_id: Optional[str] = None  # Same as registration
    preferred_theme: Optional[str] = Field(default="Default", description="User's preferred UI theme")  # Theme preference
    created_at: str  # Auto-generated timestamp
    updated_at: str  # Auto-generated timestamp
