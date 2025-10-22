"""Unit tests for services"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from backend.services.transaction_service import TransactionService
from backend.services.customer_service import CustomerService
from backend.services.user_service import UserService
from backend.exceptions import ValidationException, NotFoundError, DatabaseException, DuplicateError


class TestTransactionService:
    """Tests for TransactionService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        with patch('backend.services.transaction_service.DatabaseManager'):
            return TransactionService()
    
    def test_create_transaction_success(self, service):
        """Test successful transaction creation"""
        service.db.create_transaction = Mock(return_value="trans_123")
        
        result = service.create_transaction(
            user_id="user_1",
            items=[{"name": "item1", "qty": 1, "price": 10.0}],
            total=10.0,
            payment_method="cash"
        )
        
        assert result["id"] == "trans_123"
        assert result["user_id"] == "user_1"
        assert result["total"] == 10.0
        service.db.create_transaction.assert_called_once()
    
    def test_create_transaction_no_items(self, service):
        """Test transaction creation with no items"""
        with pytest.raises(ValidationException, match="at least one item"):
            service.create_transaction("user_1", [], 10.0)
    
    def test_create_transaction_invalid_total(self, service):
        """Test transaction creation with invalid total"""
        with pytest.raises(ValidationException, match="greater than zero"):
            service.create_transaction(
                user_id="user_1",
                items=[{"name": "item1", "qty": 1, "price": 10.0}],
                total=-5.0
            )
    
    def test_get_transaction_success(self, service):
        """Test successful transaction retrieval"""
        service.db.get_transaction_by_id = Mock(return_value={"_id": "trans_123", "total_amount": "10.0"})
        
        result = service.get_transaction("trans_123")
        
        assert result["_id"] == "trans_123"
        service.db.get_transaction_by_id.assert_called_once_with("trans_123")
    
    def test_get_transaction_not_found(self, service):
        """Test transaction retrieval when not found"""
        service.db.get_transaction_by_id = Mock(return_value=None)
        
        with pytest.raises(NotFoundError):
            service.get_transaction("trans_nonexistent")
    
    def test_get_transactions_by_user(self, service):
        """Test retrieving user transactions"""
        transactions = [{"_id": "trans_1"}, {"_id": "trans_2"}]
        service.db.get_user_transactions = Mock(return_value=transactions)
        
        result = service.get_transactions_by_user("user_1")
        
        assert len(result) == 2
        service.db.get_user_transactions.assert_called_once_with("user_1")
    
    def test_get_transaction_summary(self, service):
        """Test transaction summary generation"""
        transactions = [
            {"total_amount": "100", "created_at": datetime.now()},
            {"total_amount": "50", "created_at": datetime.now()}
        ]
        service.db.get_user_transactions = Mock(return_value=transactions)
        
        result = service.get_transaction_summary("user_1")
        
        assert result["total_transactions"] == 2
        assert result["total_revenue"] == 150
        assert result["average_transaction"] == 75


class TestCustomerService:
    """Tests for CustomerService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        with patch('backend.services.customer_service.DatabaseManager'):
            return CustomerService()
    
    def test_create_customer_success(self, service):
        """Test successful customer creation"""
        service.db.search_customers = Mock(return_value=[])
        service.db.create_customer = Mock(return_value="cust_123")
        
        result = service.create_customer(
            user_id="user_1",
            name="John Doe",
            email="john@example.com",
            phone="123456"
        )
        
        assert result["id"] == "cust_123"
        assert result["name"] == "John Doe"
        service.db.create_customer.assert_called_once()
    
    def test_create_customer_name_too_short(self, service):
        """Test customer creation with name too short"""
        with pytest.raises(ValidationException, match="2 characters"):
            service.create_customer("user_1", "J", "john@example.com")
    
    def test_create_customer_no_email(self, service):
        """Test customer creation without email"""
        with pytest.raises(ValidationException, match="Email is required"):
            service.create_customer("user_1", "John Doe", "")
    
    def test_create_customer_duplicate(self, service):
        """Test customer creation with duplicate email"""
        service.db.search_customers = Mock(return_value=[{"email": "john@example.com"}])
        
        with pytest.raises(DuplicateError):
            service.create_customer("user_1", "John Doe", "john@example.com")
    
    def test_search_customers(self, service):
        """Test customer search"""
        customers = [{"name": "John"}, {"name": "Jane"}]
        service.db.search_customers = Mock(return_value=customers)
        
        result = service.search_customers("user_1", "John")
        
        assert len(result) == 2
        service.db.search_customers.assert_called_once()


class TestUserService:
    """Tests for UserService"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        with patch('backend.services.user_service.DatabaseManager'):
            return UserService()
    
    def test_create_user_success(self, service):
        """Test successful user creation"""
        service.db.create_user = Mock(return_value="user_123")
        
        result = service.create_user(
            business_name="My Business",
            pin="1234",
            business_type="retail"
        )
        
        assert result["id"] == "user_123"
        assert result["business_name"] == "My Business"
        service.db.create_user.assert_called_once()
    
    def test_create_user_invalid_name(self, service):
        """Test user creation with invalid name"""
        with pytest.raises(ValidationException):
            service.create_user("B", "1234", "retail")
    
    def test_create_user_invalid_pin(self, service):
        """Test user creation with invalid PIN"""
        with pytest.raises(ValidationException):
            service.create_user("My Business", "123", "retail")
    
    def test_create_user_invalid_type(self, service):
        """Test user creation with invalid business type"""
        with pytest.raises(ValidationException):
            service.create_user("My Business", "1234", "invalid_type")
    
    def test_verify_credentials_success(self, service):
        """Test successful credential verification"""
        service.db.validate_pin = Mock(return_value="user_123")
        
        result = service.verify_credentials("My Business", "1234")
        
        assert result["id"] == "user_123"
        assert result["business_name"] == "My Business"
    
    def test_verify_credentials_failure(self, service):
        """Test failed credential verification"""
        service.db.validate_pin = Mock(return_value=None)
        
        result = service.verify_credentials("My Business", "wrong")
        
        assert result is None
    
    def test_get_user_success(self, service):
        """Test successful user retrieval"""
        service.db.get_user_by_id = Mock(return_value={"_id": "user_123", "business_name": "My Business"})
        
        result = service.get_user("user_123")
        
        assert result["_id"] == "user_123"
        service.db.get_user_by_id.assert_called_once_with("user_123")
    
    def test_get_user_not_found(self, service):
        """Test user retrieval when not found"""
        service.db.get_user_by_id = Mock(return_value=None)
        
        with pytest.raises(NotFoundError):
            service.get_user("user_nonexistent")


# Test execution with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
