"""FastAPI REST API for POS System"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import logging
from datetime import datetime

# Import services
from backend.services.transaction_service import TransactionService
from backend.services.customer_service import CustomerService
from backend.services.user_service import UserService
from backend.exceptions import ValidationException, NotFoundError, DatabaseException, DuplicateError
from backend.config.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Portable POS API",
    description="REST API for Portable Point-of-Sale System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TransactionItemRequest(BaseModel):
    name: str
    qty: int
    price: float

class CreateTransactionRequest(BaseModel):
    user_id: str
    items: List[TransactionItemRequest]
    total: float
    payment_method: str = "cash"
    notes: Optional[str] = ""

class CreateCustomerRequest(BaseModel):
    user_id: str
    name: str
    email: str
    phone: Optional[str] = ""
    address: Optional[str] = ""

class CreateUserRequest(BaseModel):
    business_name: str
    pin: str
    business_type: str

class LoginRequest(BaseModel):
    business_name: str
    pin: str

# Service instances
transaction_service = TransactionService()
customer_service = CustomerService()
user_service = UserService()

# ============ Health Check ============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# ============ User Endpoints ============

@app.post("/api/users", tags=["Users"])
async def create_user(request: CreateUserRequest):
    """Create new user"""
    try:
        logger.info(f"Creating user: {request.business_name}")
        result = user_service.create_user(
            request.business_name,
            request.pin,
            request.business_type
        )
        return {"success": True, "data": result}
    except ValidationException as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users/login", tags=["Users"])
async def login(request: LoginRequest):
    """Login user"""
    try:
        logger.info(f"Login attempt: {request.business_name}")
        result = user_service.verify_credentials(request.business_name, request.pin)
        if result:
            logger.info(f"Login successful: {request.business_name}")
            return {"success": True, "data": result}
        else:
            logger.warning(f"Login failed: {request.business_name}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}", tags=["Users"])
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        logger.debug(f"Retrieving user: {user_id}")
        result = user_service.get_user(user_id)
        return {"success": True, "data": result}
    except NotFoundError as e:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Transaction Endpoints ============

@app.post("/api/transactions", tags=["Transactions"])
async def create_transaction(request: CreateTransactionRequest):
    """Create new transaction"""
    try:
        logger.info(f"Creating transaction for user: {request.user_id}")
        items = [item.dict() for item in request.items]
        result = transaction_service.create_transaction(
            request.user_id,
            items,
            request.total,
            request.payment_method,
            request.notes
        )
        logger.info(f"Transaction created: {result['id']}")
        return {"success": True, "data": result}
    except ValidationException as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions/{transaction_id}", tags=["Transactions"])
async def get_transaction(transaction_id: str):
    """Get transaction by ID"""
    try:
        logger.debug(f"Retrieving transaction: {transaction_id}")
        result = transaction_service.get_transaction(transaction_id)
        return {"success": True, "data": result}
    except NotFoundError as e:
        logger.warning(f"Transaction not found: {transaction_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/transactions", tags=["Transactions"])
async def get_user_transactions(user_id: str):
    """Get all transactions for a user"""
    try:
        logger.debug(f"Retrieving transactions for user: {user_id}")
        result = transaction_service.get_transactions_by_user(user_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/transactions/summary", tags=["Transactions"])
async def get_transaction_summary(user_id: str):
    """Get transaction summary for user"""
    try:
        logger.debug(f"Generating transaction summary for user: {user_id}")
        result = transaction_service.get_transaction_summary(user_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Customer Endpoints ============

@app.post("/api/customers", tags=["Customers"])
async def create_customer(request: CreateCustomerRequest):
    """Create new customer"""
    try:
        logger.info(f"Creating customer for user: {request.user_id}")
        result = customer_service.create_customer(
            request.user_id,
            request.name,
            request.email,
            request.phone or "",
            request.address or ""
        )
        logger.info(f"Customer created: {result['id']}")
        return {"success": True, "data": result}
    except (ValidationException, DuplicateError) as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}", tags=["Customers"])
async def get_customer(customer_id: str):
    """Get customer by ID"""
    try:
        logger.debug(f"Retrieving customer: {customer_id}")
        result = customer_service.get_customer(customer_id)
        return {"success": True, "data": result}
    except NotFoundError as e:
        logger.warning(f"Customer not found: {customer_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving customer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/customers", tags=["Customers"])
async def get_user_customers(user_id: str):
    """Get all customers for a user"""
    try:
        logger.debug(f"Retrieving customers for user: {user_id}")
        result = customer_service.get_all_customers(user_id)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error retrieving customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/customers/search", tags=["Customers"])
async def search_customers(user_id: str, q: str = ""):
    """Search customers"""
    try:
        logger.debug(f"Searching customers for user: {user_id}, query: {q}")
        result = customer_service.search_customers(user_id, q)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error searching customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/summary", tags=["Customers"])
async def get_customer_summary(customer_id: str):
    """Get customer summary"""
    try:
        logger.debug(f"Generating summary for customer: {customer_id}")
        result = customer_service.get_customer_summary(customer_id)
        return {"success": True, "data": result}
    except NotFoundError as e:
        logger.warning(f"Customer not found: {customer_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Error Handlers ============

@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": str(exc)},
    )

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request, exc):
    logger.error(f"Not found error: {str(exc)}")
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": str(exc)},
    )

@app.exception_handler(DatabaseException)
async def database_exception_handler(request, exc):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)},
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
