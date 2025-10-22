"""Customer Service - Business logic for customer management"""
from typing import List, Dict, Optional
from datetime import datetime
from backend.database.mongodb import DatabaseManager
from backend.exceptions import ValidationException, NotFoundError, DatabaseException, DuplicateError
from backend.config.logging import setup_logging
import logging
import time

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class CustomerService:
    """Handle customer business logic"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.logger = logger
        logger.info("CustomerService initialized")
    
    def create_customer(self, user_id: str, name: str, email: str, phone: str = "", address: str = "") -> Dict:
        """
        Create new customer with validation
        
        Args:
            user_id: ID of user creating customer
            name: Customer name
            email: Customer email
            phone: Customer phone number
            address: Customer address
            
        Returns:
            Created customer data
            
        Raises:
            ValidationException: If validation fails
            DuplicateError: If customer already exists
            DatabaseException: If database operation fails
        """
        start_time = time.time()
        try:
            logger.debug(f"Creating customer for user {user_id}: name={name}, email={email}")
            
            # Validate
            if len(name.strip()) < 2:
                logger.warning(f"Customer creation rejected: name too short for user {user_id}")
                raise ValidationException("Customer name must be at least 2 characters")
            if len(email.strip()) == 0:
                logger.warning(f"Customer creation rejected: no email for user {user_id}")
                raise ValidationException("Email is required")
            
            # Check for duplicates
            existing = self.db.search_customers(user_id, search_term=email)
            if existing:
                elapsed_time = time.time() - start_time
                logger.warning(f"Customer creation rejected: duplicate email {email} for user {user_id}, time: {elapsed_time:.2f}s")
                raise DuplicateError(f"Customer with email {email} already exists")
            
            customer_id = self.db.create_customer(
                user_id=user_id,
                name=name.strip(),
                email=email.strip(),
                phone=phone.strip(),
                address=address.strip()
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Customer created successfully - ID: {customer_id}, user: {user_id}, "
                       f"name: {name}, email: {email}, time: {elapsed_time:.2f}s")
            
            return {
                "id": customer_id,
                "user_id": user_id,
                "name": name.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
                "address": address.strip()
            }
            
        except (ValidationException, DuplicateError) as ve:
            elapsed_time = time.time() - start_time
            logger.error(f"Validation error creating customer for user {user_id}: {str(ve)}, time: {elapsed_time:.2f}s")
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to create customer for user {user_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise DatabaseException(f"Failed to create customer: {str(e)}")
    
    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """
        Get customer by ID
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer data
            
        Raises:
            NotFoundError: If customer not found
        """
        start_time = time.time()
        try:
            logger.debug(f"Retrieving customer {customer_id}")
            customer = self.db.customers_collection.find_one({"_id": __import__("bson").objectid.ObjectId(customer_id)})
            elapsed_time = time.time() - start_time
            
            if not customer:
                logger.warning(f"Customer {customer_id} not found, time: {elapsed_time:.2f}s")
                raise NotFoundError(f"Customer {customer_id} not found")
            
            customer["_id"] = str(customer["_id"])
            logger.debug(f"Customer {customer_id} retrieved successfully, time: {elapsed_time:.2f}s")
            return customer
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to get customer {customer_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise
    
    def get_all_customers(self, user_id: str) -> List[Dict]:
        """
        Get all customers for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of customers
        """
        start_time = time.time()
        try:
            logger.debug(f"Retrieving all customers for user {user_id}")
            customers = self.db.search_customers(user_id)
            elapsed_time = time.time() - start_time
            logger.info(f"Retrieved {len(customers)} customers for user {user_id}, time: {elapsed_time:.2f}s")
            return customers
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to get customers for user {user_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise DatabaseException(f"Failed to get customers: {str(e)}")
    
    def get_customer_summary(self, customer_id: str) -> Dict:
        """
        Get customer summary with transaction history
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer summary with statistics
        """
        start_time = time.time()
        try:
            logger.debug(f"Generating summary for customer {customer_id}")
            customer = self.get_customer(customer_id)
            
            summary = {
                "customer": customer,
                "total_transactions": customer.get("total_visits", 0),
                "total_spent": float(customer.get("total_spent", 0)),
                "average_transaction": float(customer.get("total_spent", 0)) / customer.get("total_visits", 1) if customer.get("total_visits", 0) > 0 else 0
            }
            
            elapsed_time = time.time() - start_time
            logger.info(f"Summary generated for customer {customer_id}: "
                       f"visits: {summary['total_transactions']}, spent: {summary['total_spent']} MYR, time: {elapsed_time:.2f}s")
            
            return summary
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to get summary for customer {customer_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise
    
    def search_customers(self, user_id: str, search_term: str = "") -> List[Dict]:
        """
        Search customers by name, email, or phone
        
        Args:
            user_id: User ID
            search_term: Search query
            
        Returns:
            List of matching customers
        """
        start_time = time.time()
        try:
            logger.debug(f"Searching customers for user {user_id} with term: '{search_term}'")
            customers = self.db.search_customers(user_id, search_term=search_term if search_term else None)
            elapsed_time = time.time() - start_time
            logger.info(f"Found {len(customers)} customers for user {user_id} with search '{search_term}', time: {elapsed_time:.2f}s")
            return customers
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to search customers for user {user_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise DatabaseException(f"Failed to search customers: {str(e)}")
