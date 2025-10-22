# models/customer.py - Data structures for customer/member management

from pydantic import BaseModel, Field, EmailStr  # Data validation framework
from typing import Optional  # For optional fields
from datetime import datetime  # For timestamps

class CustomerCreateRequest(BaseModel):
    """What the user sends when adding a new customer/member"""
    
    # Basic customer info
    name: str = Field(..., min_length=1, max_length=100, description="Customer name")
    
    # Contact information (at least one required)
    phone: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=20,
        description="Phone number for SMS marketing"
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address for email marketing"
    )
    
    # Optional customer details
    birthday: Optional[str] = Field(
        default=None,
        description="Birthday in YYYY-MM-DD format for special offers"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Customer notes (preferences, allergies, etc.)"
    )

class CustomerUpdateRequest(BaseModel):
    """What the user sends when updating customer info"""
    
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    email: Optional[str] = Field(default=None)
    birthday: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=200)
    is_active: Optional[bool] = Field(default=None, description="Active member status")

class CustomerInDB(BaseModel):
    """How customer data is stored in MongoDB"""
    
    id: str = Field(..., alias="_id", description="Unique customer ID")
    user_id: str  # Which business this customer belongs to
    
    # Customer details
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    notes: Optional[str] = None
    
    # Member status and stats
    is_active: bool = Field(default=True, description="Active member status")
    total_visits: int = Field(default=0, description="Number of transactions")
    total_spent: str = Field(default="0.00", description="Total amount spent (lifetime value)")
    last_visit: Optional[str] = Field(default=None, description="Last transaction date")
    
    # Marketing preferences
    sms_marketing: bool = Field(default=True, description="Opt-in for SMS marketing")
    email_marketing: bool = Field(default=True, description="Opt-in for email marketing")
    
    # Timestamps
    created_at: str  # When customer was added
    updated_at: str  # Last update timestamp
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "60f1a1b2c3d4e5f6a7b8c9d0",
                "name": "Ahmad Rahman",
                "phone": "+60123456789",
                "email": "ahmad@email.com",
                "birthday": "1990-05-15",
                "notes": "Prefers less spicy food",
                "is_active": True,
                "total_visits": 5,
                "total_spent": "127.50",
                "last_visit": "2024-10-14",
                "sms_marketing": True,
                "email_marketing": True,
                "created_at": "2024-10-01T10:00:00Z",
                "updated_at": "2024-10-14T15:30:00Z"
            }
        }

class CustomerSearchResult(BaseModel):
    """Customer info for search/selection purposes"""
    
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    total_visits: int
    total_spent: str
    last_visit: Optional[str] = None