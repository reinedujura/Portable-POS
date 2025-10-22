"""User Service - Business logic for user management"""
from typing import Optional, Dict
from datetime import datetime
from backend.database.mongodb import DatabaseManager
from backend.exceptions import ValidationException, NotFoundError, DatabaseException, DuplicateError
from backend.config.logging import setup_logging
import logging
import time

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class UserService:
    """Handle user business logic"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.logger = logger
        logger.info("UserService initialized")
    
    def create_user(self, business_name: str, pin: str, business_type: str) -> Dict:
        """
        Create new user
        
        Args:
            business_name: Name of business
            pin: PIN code for login
            business_type: Type of business
            
        Returns:
            Created user data
            
        Raises:
            ValidationException: If validation fails
            DatabaseException: If database operation fails
        """
        start_time = time.time()
        try:
            logger.debug(f"Creating user: {business_name}, type: {business_type}")
            
            # Validate
            if len(business_name.strip()) < 2:
                logger.warning(f"User creation rejected: business name too short")
                raise ValidationException("Business name must be at least 2 characters")
            if len(pin) < 4:
                logger.warning(f"User creation rejected: PIN too short for {business_name}")
                raise ValidationException("PIN must be at least 4 characters")
            if business_type not in ["street_vendor", "tutor", "yoga_teacher", "consultant", "retail", "service"]:
                logger.warning(f"User creation rejected: invalid business type {business_type}")
                raise ValidationException(f"Invalid business type: {business_type}")
            
            # Create user
            user_id = self.db.create_user(
                business_name=business_name.strip(),
                pin=pin,
                business_type=business_type
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"User created successfully - ID: {user_id}, business: {business_name}, "
                       f"type: {business_type}, time: {elapsed_time:.2f}s")
            
            return {
                "id": user_id,
                "business_name": business_name.strip(),
                "business_type": business_type,
                "created_at": datetime.now().isoformat()
            }
            
        except (ValidationException, DuplicateError) as ve:
            elapsed_time = time.time() - start_time
            logger.error(f"Validation error creating user {business_name}: {str(ve)}, time: {elapsed_time:.2f}s")
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to create user {business_name}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    def verify_credentials(self, business_name: str, pin: str) -> Optional[Dict]:
        """
        Verify user credentials
        
        Args:
            business_name: Business name
            pin: PIN code
            
        Returns:
            User data if credentials valid, None otherwise
        """
        start_time = time.time()
        try:
            logger.debug(f"Verifying credentials for: {business_name}")
            user_id = self.db.validate_pin(business_name, pin)
            elapsed_time = time.time() - start_time
            
            if user_id:
                logger.info(f"User logged in successfully - business: {business_name}, user_id: {user_id}, time: {elapsed_time:.2f}s")
                return {"id": user_id, "business_name": business_name}
            
            logger.warning(f"Failed login attempt for {business_name}, time: {elapsed_time:.2f}s")
            return None
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to verify credentials for {business_name}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise DatabaseException(f"Failed to verify credentials: {str(e)}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User data
            
        Raises:
            NotFoundError: If user not found
        """
        start_time = time.time()
        try:
            logger.debug(f"Retrieving user {user_id}")
            user = self.db.get_user_by_id(user_id)
            elapsed_time = time.time() - start_time
            
            if not user:
                logger.warning(f"User {user_id} not found, time: {elapsed_time:.2f}s")
                raise NotFoundError(f"User {user_id} not found")
            
            logger.debug(f"User {user_id} retrieved successfully, time: {elapsed_time:.2f}s")
            return user
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to get user {user_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise
