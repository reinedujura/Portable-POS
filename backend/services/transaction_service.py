"""Transaction Service - Business logic for transaction management"""
from typing import List, Dict, Optional
from datetime import datetime
from backend.database.mongodb import DatabaseManager
from backend.exceptions import ValidationException, NotFoundError, DatabaseException
from backend.config.logging import setup_logging
import logging
import time

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class TransactionService:
    """Handle transaction business logic"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.logger = logger
        logger.info("TransactionService initialized")
    
    def create_transaction(self, user_id: str, items: List[Dict], total: float, 
                          payment_method: str = "cash", notes: str = "") -> Dict:
        """
        Create new transaction with validation
        
        Args:
            user_id: ID of user creating transaction
            items: List of transaction items
            total: Total amount
            payment_method: Payment method (cash, card, etc.)
            notes: Transaction notes
            
        Returns:
            Created transaction data
            
        Raises:
            ValidationException: If validation fails
            DatabaseException: If database operation fails
        """
        start_time = time.time()
        try:
            logger.debug(f"Creating transaction for user {user_id}, items count: {len(items)}, total: {total}")
            
            # Validate input
            if not items:
                logger.warning(f"Transaction creation rejected: no items provided by user {user_id}")
                raise ValidationException("Transaction must have at least one item")
            if total <= 0:
                logger.warning(f"Transaction creation rejected: invalid total {total} for user {user_id}")
                raise ValidationException("Total must be greater than zero")
            if len(payment_method.strip()) == 0:
                logger.warning(f"Transaction creation rejected: no payment method for user {user_id}")
                raise ValidationException("Payment method required")
            
            # Calculate item total for verification
            calculated_total = sum(item.get("price", 0) * item.get("qty", 1) for item in items)
            if abs(calculated_total - total) > 0.01:  # Allow for rounding
                logger.warning(f"Total mismatch for user {user_id}: calculated={calculated_total}, provided={total}")
            
            # Create transaction
            transaction_data = {
                "items": items,
                "total_amount": str(total),
                "currency": "MYR",
                "customer_name": None,
                "customer_id": None,
                "notes": notes,
            }
            
            result_id = self.db.create_transaction(user_id, items, str(total), notes=notes)
            elapsed_time = time.time() - start_time
            
            logger.info(f"Transaction created successfully - ID: {result_id}, user: {user_id}, "
                       f"amount: {total} MYR, time: {elapsed_time:.2f}s")
            
            return {
                "id": result_id,
                "user_id": user_id,
                "items": items,
                "total": total,
                "payment_method": payment_method,
                "notes": notes,
                "created_at": datetime.now().isoformat()
            }
            
        except ValidationException as ve:
            elapsed_time = time.time() - start_time
            logger.error(f"Validation error creating transaction for user {user_id}: {str(ve)}, time: {elapsed_time:.2f}s")
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to create transaction for user {user_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise DatabaseException(f"Failed to create transaction: {str(e)}")
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """
        Get transaction by ID
        
        Args:
            transaction_id: ID of transaction to retrieve
            
        Returns:
            Transaction data or None
            
        Raises:
            NotFoundError: If transaction not found
        """
        start_time = time.time()
        try:
            logger.debug(f"Retrieving transaction {transaction_id}")
            transaction = self.db.get_transaction_by_id(transaction_id)
            elapsed_time = time.time() - start_time
            
            if not transaction:
                logger.warning(f"Transaction {transaction_id} not found, time: {elapsed_time:.2f}s")
                raise NotFoundError(f"Transaction {transaction_id} not found")
            
            logger.debug(f"Transaction {transaction_id} retrieved successfully, time: {elapsed_time:.2f}s")
            return transaction
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to get transaction {transaction_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise
    
    def get_transactions_by_user(self, user_id: str) -> List[Dict]:
        """
        Get all transactions for a user
        
        Args:
            user_id: ID of user
            
        Returns:
            List of transactions
        """
        start_time = time.time()
        try:
            logger.debug(f"Retrieving transactions for user {user_id}")
            transactions = self.db.get_user_transactions(user_id)
            elapsed_time = time.time() - start_time
            logger.info(f"Retrieved {len(transactions)} transactions for user {user_id}, time: {elapsed_time:.2f}s")
            return transactions
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to get transactions for user {user_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise DatabaseException(f"Failed to get transactions: {str(e)}")
    
    def get_transaction_summary(self, user_id: str) -> Dict:
        """
        Get transaction analytics for user
        
        Args:
            user_id: ID of user
            
        Returns:
            Dictionary with transaction summary
        """
        start_time = time.time()
        try:
            logger.debug(f"Generating transaction summary for user {user_id}")
            transactions = self.get_transactions_by_user(user_id)
            
            if not transactions:
                logger.info(f"No transactions found for user {user_id}")
                return {
                    "total_transactions": 0,
                    "total_revenue": 0,
                    "average_transaction": 0,
                    "daily_breakdown": {}
                }
            
            total_revenue = sum(float(t.get("total_amount", 0)) for t in transactions)
            avg_transaction = total_revenue / len(transactions)
            
            summary = {
                "total_transactions": len(transactions),
                "total_revenue": total_revenue,
                "average_transaction": avg_transaction,
                "daily_breakdown": self._calculate_daily_breakdown(transactions)
            }
            
            elapsed_time = time.time() - start_time
            logger.info(f"Summary generated for user {user_id}: {len(transactions)} transactions, "
                       f"revenue: {total_revenue} MYR, avg: {avg_transaction:.2f} MYR, time: {elapsed_time:.2f}s")
            
            return summary
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Failed to get summary for user {user_id}: {str(e)}, time: {elapsed_time:.2f}s", 
                        exc_info=True)
            raise
    
    def _calculate_daily_breakdown(self, transactions: List[Dict]) -> Dict:
        """Calculate daily breakdown of transactions"""
        daily = {}
        for transaction in transactions:
            created_at = transaction.get("created_at")
            if isinstance(created_at, datetime):
                date_key = created_at.date().isoformat()
            else:
                date_key = str(created_at)[:10]
            
            if date_key not in daily:
                daily[date_key] = {"count": 0, "total": 0}
            daily[date_key]["count"] += 1
            daily[date_key]["total"] += float(transaction.get("total_amount", 0))
        return daily
