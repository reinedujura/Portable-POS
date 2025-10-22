"""Integration tests for services with database"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from backend.services.transaction_service import TransactionService
from backend.services.customer_service import CustomerService
from backend.services.user_service import UserService


class TestTransactionIntegration:
    """Integration tests for TransactionService with database"""
    
    @pytest.fixture
    def service(self):
        """Create service with mocked database"""
        with patch('backend.services.transaction_service.DatabaseManager') as mock_db:
            service = TransactionService()
            service.db = mock_db
            return service
    
    def test_complete_transaction_flow(self, service):
        """Test complete transaction workflow"""
        # Setup
        service.db.create_transaction = MagicMock(return_value="trans_001")
        service.db.get_transaction_by_id = MagicMock(return_value={
            "_id": "trans_001",
            "user_id": "user_1",
            "total_amount": "100",
            "items": [{"name": "item1", "qty": 1, "price": 100}]
        })
        service.db.get_user_transactions = MagicMock(return_value=[
            {
                "_id": "trans_001",
                "total_amount": "100",
                "created_at": datetime.now()
            }
        ])
        
        # Create transaction
        created = service.create_transaction(
            user_id="user_1",
            items=[{"name": "item1", "qty": 1, "price": 100}],
            total=100,
            payment_method="cash"
        )
        assert created["id"] == "trans_001"
        
        # Retrieve transaction
        retrieved = service.get_transaction("trans_001")
        assert retrieved["total_amount"] == "100"
        
        # Get user transactions
        transactions = service.get_transactions_by_user("user_1")
        assert len(transactions) == 1
        
        # Get summary
        summary = service.get_transaction_summary("user_1")
        assert summary["total_transactions"] == 1
        assert summary["total_revenue"] == 100
    
    def test_transaction_error_recovery(self, service):
        """Test error handling and recovery"""
        service.db.create_transaction = MagicMock(side_effect=Exception("DB Error"))
        
        # Should raise DatabaseException
        from backend.exceptions import DatabaseException
        with pytest.raises(DatabaseException):
            service.create_transaction("user_1", [{"name": "item", "qty": 1, "price": 10}], 10)


class TestCustomerIntegration:
    """Integration tests for CustomerService with database"""
    
    @pytest.fixture
    def service(self):
        """Create service with mocked database"""
        with patch('backend.services.customer_service.DatabaseManager') as mock_db:
            service = CustomerService()
            service.db = mock_db
            return service
    
    def test_complete_customer_flow(self, service):
        """Test complete customer workflow"""
        # Setup
        service.db.search_customers = MagicMock(return_value=[])
        service.db.create_customer = MagicMock(return_value="cust_001")
        service.db.customers_collection.find_one = MagicMock(return_value={
            "_id": MagicMock(),
            "name": "John Doe",
            "email": "john@example.com",
            "total_visits": 5,
            "total_spent": "500"
        })
        
        # Create customer
        created = service.create_customer(
            user_id="user_1",
            name="John Doe",
            email="john@example.com",
            phone="123456"
        )
        assert created["id"] == "cust_001"
        
        # Search customers
        service.db.search_customers = MagicMock(return_value=[
            {"_id": "cust_001", "name": "John Doe"}
        ])
        results = service.search_customers("user_1", "John")
        assert len(results) == 1
    
    def test_customer_duplicate_prevention(self, service):
        """Test that duplicate customers are prevented"""
        from backend.exceptions import DuplicateError
        
        service.db.search_customers = MagicMock(return_value=[
            {"email": "john@example.com"}
        ])
        
        with pytest.raises(DuplicateError):
            service.create_customer("user_1", "John Doe", "john@example.com")


class TestUserIntegration:
    """Integration tests for UserService with database"""
    
    @pytest.fixture
    def service(self):
        """Create service with mocked database"""
        with patch('backend.services.user_service.DatabaseManager') as mock_db:
            service = UserService()
            service.db = mock_db
            return service
    
    def test_complete_user_flow(self, service):
        """Test complete user workflow"""
        # Setup
        service.db.create_user = MagicMock(return_value="user_001")
        service.db.validate_pin = MagicMock(return_value="user_001")
        service.db.get_user_by_id = MagicMock(return_value={
            "_id": "user_001",
            "business_name": "My Shop",
            "business_type": "retail"
        })
        
        # Create user
        created = service.create_user(
            business_name="My Shop",
            pin="1234",
            business_type="retail"
        )
        assert created["id"] == "user_001"
        
        # Verify credentials
        verified = service.verify_credentials("My Shop", "1234")
        assert verified["id"] == "user_001"
        
        # Get user
        user = service.get_user("user_001")
        assert user["business_name"] == "My Shop"
    
    def test_user_authentication_flow(self, service):
        """Test user authentication workflow"""
        service.db.create_user = MagicMock(return_value="user_001")
        service.db.validate_pin = MagicMock(return_value=None)  # Wrong password
        
        # Create user
        created = service.create_user("My Shop", "1234", "retail")
        assert created["id"] == "user_001"
        
        # Try wrong credentials
        verified = service.verify_credentials("My Shop", "wrong")
        assert verified is None


class TestCrossServiceIntegration:
    """Integration tests across multiple services"""
    
    @pytest.fixture
    def services(self):
        """Create all service instances"""
        with patch('backend.services.transaction_service.DatabaseManager'), \
             patch('backend.services.customer_service.DatabaseManager'), \
             patch('backend.services.user_service.DatabaseManager'):
            return {
                'transaction': TransactionService(),
                'customer': CustomerService(),
                'user': UserService()
            }
    
    def test_user_creates_transaction_with_customer(self, services):
        """Test user creating transaction with customer"""
        # Create user
        services['user'].db.create_user = MagicMock(return_value="user_001")
        user = services['user'].create_user("My Shop", "1234", "retail")
        assert user["id"] == "user_001"
        
        # Create customer
        services['customer'].db.search_customers = MagicMock(return_value=[])
        services['customer'].db.create_customer = MagicMock(return_value="cust_001")
        customer = services['customer'].create_customer(
            user_id="user_001",
            name="John",
            email="john@example.com"
        )
        assert customer["id"] == "cust_001"
        
        # Create transaction
        services['transaction'].db.create_transaction = MagicMock(return_value="trans_001")
        transaction = services['transaction'].create_transaction(
            user_id="user_001",
            items=[{"name": "item", "qty": 1, "price": 100}],
            total=100
        )
        assert transaction["id"] == "trans_001"


class TestErrorHandling:
    """Test error handling across services"""
    
    def test_database_connection_error(self):
        """Test handling of database connection errors"""
        with patch('backend.services.transaction_service.DatabaseManager') as mock_db:
            mock_db.side_effect = Exception("Connection refused")
            
            # Service initialization should not fail
            # but operations should
            with patch.object(TransactionService, '__init__', return_value=None):
                service = TransactionService()
    
    def test_validation_error_propagation(self):
        """Test that validation errors propagate correctly"""
        with patch('backend.services.user_service.DatabaseManager'):
            service = UserService()
            
            from backend.exceptions import ValidationException
            
            with pytest.raises(ValidationException):
                service.create_user("", "1234", "retail")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
