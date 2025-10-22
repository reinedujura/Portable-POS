# mongodb.py - MongoDB manager for Portable POS
from pymongo import MongoClient  # MongoDB driver
from datetime import datetime, timedelta  # For timestamps and date calculations
from bson.objectid import ObjectId  # For MongoDB IDs
from dotenv import load_dotenv  # Load .env variables
import os  # For environment variables
import bcrypt  # For secure PIN hashing
from typing import Optional, List, Dict, Any, Union  # Type hints for better code clarity

load_dotenv()  # Load environment variables from .env file

# ========================================================================
# CUSTOM EXCEPTION CLASSES
# ========================================================================

class DatabaseException(Exception):
    """Base exception for database operations"""
    pass

class ValidationException(DatabaseException):
    """Raised when data validation fails"""
    pass

class NotFoundError(DatabaseException):
    """Raised when a requested resource is not found"""
    pass

class DuplicateError(DatabaseException):
    """Raised when attempting to create a duplicate entry"""
    pass

# ========================================================================
# MONGODB CONFIGURATION
# ========================================================================

mongo_uri = os.getenv("MONGODB_ATLAS_CLUSTER_URI")  # Get MongoDB connection string

class DatabaseManager:
    def __init__(self, db_name: str = "portable_pos_db", connection_string: Optional[str] = mongo_uri) -> None:  # Changed to portable_pos_db
        self.client: MongoClient = MongoClient(connection_string)  # Connect to MongoDB
        self.db: Any = self.client[db_name]  # Select database
        self.users_collection: Any = self.db["users"]  # Collection for user accounts
        self.transactions_collection: Any = self.db["transactions"]  # Collection for sales transactions
        self.menu_items_collection: Any = self.db["menu_items"]  # Collection for products/services (menu items)
        self.customers_collection: Any = self.db["customers"]  # Collection for customer/member management
        self.quotations_collection: Any = self.db["quotations"]  # Collection for quotations
        self.documents_collection: Any = self.db["documents"]  # Collection for invoices, receipts, delivery orders
        self.init_database()  # Set up indexes

    
    def init_database(self) -> None:
        """Initialize database with collections and indexes"""
        # Create unique index on business_name for users (one account per business name)
        self.users_collection.create_index("business_name", unique=True)
        # Create index on user_id for transactions (fast lookup of user's sales history)
        self.transactions_collection.create_index("user_id")
        # Create index on user_id for menu items (fast lookup of user's products/services)
        self.menu_items_collection.create_index("user_id")
        # Create index on user_id for quotations (fast lookup of user's quotations)
        self.quotations_collection.create_index("user_id")
        # Create index on quotation_number for fast lookup
        self.quotations_collection.create_index([("user_id", 1), ("quotation_number", 1)], unique=True)
        # Create index on user_id for documents (fast lookup of user's documents)
        self.documents_collection.create_index("user_id")
        # Create index on document_number for fast lookup
        self.documents_collection.create_index([("user_id", 1), ("document_number", 1)], unique=True)
        # Create index on user_id for customers (fast lookup of user's customers)
        self.customers_collection.create_index("user_id")
        # Create indexes for customer search (phone and email)
        self.customers_collection.create_index("phone")
        self.customers_collection.create_index("email")

    def _ensure_object_id(self, value: Union[str, ObjectId, Any]) -> Union[ObjectId, Any]:
        """Convert string to ObjectId if valid, else return as-is.
        
        This consolidates the repeated ObjectId conversion pattern used throughout the file.
        
        Args:
            value: String or value to potentially convert
            
        Returns:
            ObjectId if value is valid ObjectId string, otherwise returns value as-is
            
        Example:
            user_oid = self._ensure_object_id(user_id)
            # If user_id is valid ObjectId string: returns ObjectId instance
            # Otherwise: returns original user_id
        """
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        return value

    def _build_user_id_query(self, user_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Build a query that handles both ObjectId and string user_id formats.
        
        MongoDB queries may have user_id stored as either ObjectId or string.
        This helper consolidates the common pattern of checking both formats.
        
        Args:
            user_id: User ID in string or ObjectId format
            
        Returns:
            MongoDB query matching either format
            
        Example:
            query = {"$or": [self._build_user_id_query(user_id), {"status": "active"}]}
        """
        user_object_id = self._ensure_object_id(user_id)
        return {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]}

    def _build_active_filter(self) -> Dict[str, Any]:
        """Build a query filter for active records (handles missing is_active field).
        
        Some legacy records may not have the is_active field.
        This helper consolidates the common pattern of checking both:
        - is_active: True
        - Missing is_active field
        
        Returns:
            MongoDB query matching active records
            
        Example:
            query = {"$and": [self._build_user_id_query(uid), self._build_active_filter()]}
        """
        return {
            "$or": [
                {"is_active": True},
                {"is_active": {"$exists": False}}
            ]
        }

    def _build_customer_search_query(self, user_id: Union[str, ObjectId], phone: Optional[str] = None, 
                                    email: Optional[str] = None) -> Dict[str, Any]:
        """Build a comprehensive customer search query.
        
        Consolidates common pattern for searching customers by:
        - User (handles both ObjectId and string formats)
        - Active status (handles missing is_active field)
        - Contact info (phone and/or email)
        
        Args:
            user_id: User ID in string or ObjectId format
            phone: Optional phone number to search
            email: Optional email to search
            
        Returns:
            MongoDB query for finding matching customers
            
        Raises:
            ValidationException: If neither phone nor email provided
            
        Example:
            query = self._build_customer_search_query(user_id, phone="1234567890")
        """
        if not phone and not email:
            raise ValidationException("Either phone or email must be provided for customer search")
            
        user_object_id = self._ensure_object_id(user_id)
        
        # Build contact query
        if phone and email:
            contact_query = {"$or": [{"phone": phone}, {"email": email}]}
        elif phone:
            contact_query = {"phone": phone}
        else:
            contact_query = {"email": email}
        
        # Combine all query components
        return {
            "$and": [
                {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]},
                self._build_active_filter(),
                contact_query
            ]
        }

    # ========================================================================
    # USER MANAGEMENT FUNCTIONS
    # ========================================================================
    
    def create_user(self, business_name: str, pin: str, business_type: str,  # Create new user account
                    base_currency: str = 'MYR', business_address: Optional[str] = None,
                    tax_id: Optional[str] = None) -> Optional[str]:
        """Create a new user with hashed PIN"""
        try:
            # Hash the PIN before storing (security best practice - never store raw PIN!)
            pin_hash = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user_doc = {
                "business_name": business_name,  # Business name (e.g., "Maria's Tacos")
                "pin_hash": pin_hash,  # Hashed PIN (never store raw PIN!)
                "business_type": business_type,  # One of: street_vendor, tutor, yoga_teacher, consultant
                "base_currency": base_currency,  # User's local currency (default: MYR - Malaysian Ringgit)
                "business_address": business_address,  # Optional: for receipts
                "tax_id": tax_id,  # Optional: for legal receipts
                "created_at": datetime.now(),  # When account was created
                "updated_at": datetime.now()  # Last update time
            }
            result = self.users_collection.insert_one(user_doc)  # Insert into MongoDB
            return str(result.inserted_id)  # Return new user's ID
        except ValueError as e:
            raise ValidationException(f"Invalid user data: {str(e)}")
        except Exception as e:  # Catch other database errors
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    def validate_pin(self, business_name: str, pin: str) -> Optional[str]:  # Check if PIN is correct for login
        """Validate user PIN for login - returns user_id if valid, None if invalid"""
        try:
            # Find user by business_name
            user = self.users_collection.find_one({"business_name": business_name})
            
            if not user:  # User doesn't exist
                raise NotFoundError(f"User with business name '{business_name}' not found")
            
            # Compare provided PIN with stored hash
            if bcrypt.checkpw(pin.encode('utf-8'), user['pin_hash'].encode('utf-8')):
                return str(user['_id'])  # Return user_id if PIN matches
            
            raise ValidationException("Invalid PIN provided")
        except (NotFoundError, ValidationException):
            raise  # Re-raise custom exceptions
        except Exception as e:  # Catch other database errors
            raise DatabaseException(f"Error during PIN validation: {str(e)}")

    # ========================================================================
    # TRANSACTION MANAGEMENT FUNCTIONS
    # ========================================================================
    
    def get_user_transactions(self, user_id: str) -> List[Dict[str, Any]]:  # Get all transactions for a user
        """Get all transactions for a specific user (sales history)"""
        try:
            # Validate user_id parameter
            if not user_id:
                raise ValidationException("user_id cannot be empty")
                
            # Convert string user_id to ObjectId if it's a valid ObjectId
            user_object_id = self._ensure_object_id(user_id)

            transactions = list(self.transactions_collection.find(
                {"user_id": user_object_id}
            ).sort("created_at", -1))  # Sort by newest first
            
            # Convert ObjectId to string for JSON compatibility
            for transaction in transactions:
                transaction["_id"] = str(transaction["_id"])
                transaction["user_id"] = str(transaction["user_id"])

            return transactions  # Return list of transactions
        except ValidationException:
            raise  # Re-raise validation errors
        except Exception as e:  # Catch database errors
            raise DatabaseException(f"Failed to fetch transactions for user {user_id}: {str(e)}")

# Read Function:
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            users = list(self.users_collection.find())
            # Convert ObjectId to string for display
            for user in users:
                user["_id"] = str(user["_id"])
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

# Delete Function:
    def delete_user(self, user_id: str) -> bool:
        """Delete user and their posts"""
        try:
            # Validate user_id
            if not user_id:
                raise ValidationException("user_id cannot be empty")
                
            # Convert string user_id to ObjectId if it's a valid ObjectId
            user_object_id = self._ensure_object_id(user_id)

            # Delete user's transactions first
            self.transactions_collection.delete_many({"user_id": user_object_id})
            
            # Delete user's menu items
            self.menu_items_collection.delete_many({"user_id": user_object_id})

            # Then delete the user
            result = self.users_collection.delete_one({"_id": user_object_id})
            
            if result.deleted_count == 0:
                raise NotFoundError(f"User with ID {user_id} not found")
                
            return True
        except (ValidationException, NotFoundError):
            raise  # Re-raise custom exceptions
        except Exception as e:
            raise DatabaseException(f"Failed to delete user {user_id}: {str(e)}")

    def get_transaction_by_id(self, transaction_id: str):
        """Get a specific transaction by its ID"""
        try:
            # Convert string transaction_id to ObjectId for database query
            transaction_object_id = ObjectId(transaction_id) if ObjectId.is_valid(transaction_id) else transaction_id
            
            # Find the transaction by ID
            transaction = self.transactions_collection.find_one({"_id": transaction_object_id})
            
            if transaction:
                # Convert MongoDB ObjectId to string
                transaction["_id"] = str(transaction["_id"])
                return transaction
            else:
                return None  # Transaction not found
                
        except Exception as e:
            print(f"Error getting transaction by ID: {e}")  # Log the error for debugging
            return None  # Return None if query failed

    # ========================================================================
    # MENU ITEM MANAGEMENT FUNCTIONS (products/services)
    # ========================================================================
    
    def create_menu_item(self, user_id: str, name: str, price: str, category: str,
                       description: Optional[str] = None, stock_quantity: Optional[int] = None, 
                       is_active: bool = True, allow_duplicates: bool = False) -> Optional[str]:
        """Create a new menu item (product/service) for a user"""
        try:
            # Validate required fields
            if not user_id or not name or not price or not category:
                raise ValidationException("user_id, name, price, and category are required")
            
            # Check for duplicates unless explicitly allowed
            if not allow_duplicates:
                existing_item = self.menu_items_collection.find_one({
                    "user_id": user_id,
                    "name": {"$regex": f"^{name}$", "$options": "i"}  # Case-insensitive exact match
                })
                if existing_item:
                    print(f"⚠️  Menu item '{name}' already exists for this business. Skipping duplicate creation.")
                    return str(existing_item["_id"])  # Return existing item ID
            
            # Build the menu item document to save in MongoDB
            menu_item_doc = {
                "user_id": user_id,  # Which business owns this menu item
                "name": name,  # Product/service name (e.g., "Nasi Lemak")
                "price": price,  # Price as string (e.g., "8.50")
                "category": category,  # One of: food_drink, service, retail, digital, other
                "description": description,  # Optional detailed description
                "stock_quantity": stock_quantity,  # None = unlimited, number = limited stock
                "is_active": is_active,  # True = currently selling, False = temporarily disabled
                "created_at": datetime.now(),  # When this menu item was created
                "updated_at": datetime.now()   # When this menu item was last modified
            }
            
            # Insert into MongoDB and get the new menu item's ID
            result = self.menu_items_collection.insert_one(menu_item_doc)
            return str(result.inserted_id)  # Return the new menu item's ID as a string
            
        except ValidationException:
            raise  # Re-raise validation errors
        except Exception as e:
            raise DatabaseException(f"Failed to create menu item: {str(e)}")
    
    def get_user_menu_items(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all menu items for a specific user/business"""
        try:
            # Convert string user_id to ObjectId for database query
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Find all menu items that belong to this user (query both string and ObjectId formats)
            # This handles both legacy ObjectId data and new string-based user_id data
            menu_items = list(self.menu_items_collection.find(
                {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]}
            ))
            
            # Convert MongoDB ObjectId to string for each menu item
            for menu_item in menu_items:
                menu_item["_id"] = str(menu_item["_id"])  # Convert ObjectId to string
                
            return menu_items  # Return list of menu items (empty list if none found)
            
        except Exception as e:
            print(f"Error getting user menu items: {e}")  # Log the error for debugging
            return []  # Return empty list if query failed
    
    def update_menu_item(self, menu_item_id: str, **updates: Any) -> bool:
        """Update an existing menu item with new values"""
        try:
            # Add updated timestamp to any changes
            updates["updated_at"] = datetime.now()
            
            # Update the menu item in MongoDB
            result = self.menu_items_collection.update_one(
                {"_id": ObjectId(menu_item_id)},  # Find menu item by ID
                {"$set": updates}  # Apply the updates
            )
            
            return result.modified_count > 0  # Return True if something was updated
            
        except Exception as e:
            print(f"Error updating menu item: {e}")  # Log the error for debugging
            return False  # Return False if update failed
    
    def delete_menu_item(self, menu_item_id: str) -> bool:
        """Delete a menu item completely"""
        try:
            # Remove the menu item from MongoDB
            result = self.menu_items_collection.delete_one({"_id": ObjectId(menu_item_id)})
            
            return result.deleted_count > 0  # Return True if something was deleted
            
        except Exception as e:
            print(f"Error deleting menu item: {e}")  # Log the error for debugging
            return False  # Return False if deletion failed

    # ========================================================================
    # BACKWARD COMPATIBILITY METHODS (DEPRECATED)
    # ========================================================================
    
    def create_offering(self, *args, **kwargs):
        """DEPRECATED: Use create_menu_item() instead"""
        return self.create_menu_item(*args, **kwargs)
    
    def remove_duplicate_menu_items(self, user_id: str):
        """Remove duplicate menu items for a user, keeping the oldest version of each"""
        try:
            from collections import defaultdict
            
            # Get all menu items for the user
            menu_items = list(self.menu_items_collection.find({"user_id": user_id}))
            
            # Group by name (case-insensitive)
            items_by_name = defaultdict(list)
            for item in menu_items:
                items_by_name[item['name'].lower()].append(item)
            
            # Find and remove duplicates
            duplicates_removed = 0
            for name_lower, items in items_by_name.items():
                if len(items) > 1:
                    # Sort by created_at to keep the oldest
                    items.sort(key=lambda x: x.get('created_at', datetime.min))
                    
                    # Delete all but the first (oldest)
                    for item in items[1:]:
                        result = self.menu_items_collection.delete_one({"_id": item["_id"]})
                        if result.deleted_count > 0:
                            duplicates_removed += 1
            
            return duplicates_removed
            
        except Exception as e:
            print(f"Error removing duplicates: {e}")
            return 0
    
    def get_user_offerings(self, *args, **kwargs):
        """DEPRECATED: Use get_user_menu_items() instead"""
        return self.get_user_menu_items(*args, **kwargs)
    
    def update_offering(self, *args, **kwargs):
        """DEPRECATED: Use update_menu_item() instead"""
        return self.update_menu_item(*args, **kwargs)
    
    def delete_offering(self, *args, **kwargs):
        """DEPRECATED: Use delete_menu_item() instead"""
        return self.delete_menu_item(*args, **kwargs)

    # ========================================================================
    # CATEGORY MANAGEMENT FUNCTIONS
    # ========================================================================
    
    def get_user_categories(self, user_id: str):
        """Get all unique categories used by a user's menu items"""
        try:
            # Use aggregation to get unique categories
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$category"}},
                {"$sort": {"_id": 1}}
            ]
            
            categories = list(self.menu_items_collection.aggregate(pipeline))
            return [cat["_id"] for cat in categories if cat["_id"]]
            
        except Exception as e:
            print(f"Error getting user categories: {e}")
            return []
    
    def add_custom_category(self, user_id: str, category_name: str):
        """Add a custom category by creating a placeholder menu item (to be removed after use)"""
        try:
            # Validate category name
            if not category_name or len(category_name.strip()) == 0:
                return False
                
            category_name = category_name.strip().lower().replace(' ', '_')
            
            # Check if category already exists
            existing_categories = self.get_user_categories(user_id)
            if category_name in existing_categories:
                return True  # Category already exists
            
            # Create a temporary placeholder item to establish the category
            temp_item = {
                "user_id": user_id,
                "name": f"__TEMP_CATEGORY_PLACEHOLDER_{category_name}__",
                "price": "0.00",
                "category": category_name,
                "description": "Temporary placeholder - will be removed",
                "is_active": False,
                "created_at": datetime.utcnow()
            }
            
            result = self.menu_items_collection.insert_one(temp_item)
            return bool(result.inserted_id)
            
        except Exception as e:
            print(f"Error adding custom category: {e}")
            return False
    
    def rename_category(self, user_id: str, old_category: str, new_category: str) -> bool:
        """Rename a category for all menu items that use it"""
        try:
            if not old_category or not new_category:
                return False
                
            new_category = new_category.strip().lower().replace(' ', '_')
            
            # Update all menu items with the old category
            result = self.menu_items_collection.update_many(
                {"user_id": user_id, "category": old_category},
                {"$set": {"category": new_category}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error renaming category: {e}")
            return False
    
    def delete_category(self, user_id: str, category_name: str) -> bool:
        """Delete a category and move all items to 'other' category"""
        try:
            if not category_name:
                return False
                
            # Update all menu items with this category to 'other'
            result = self.menu_items_collection.update_many(
                {"user_id": user_id, "category": category_name},
                {"$set": {"category": "other"}}
            )
            
            # Remove any temporary placeholder items for this category
            self.menu_items_collection.delete_many({
                "user_id": user_id,
                "name": {"$regex": f"__TEMP_CATEGORY_PLACEHOLDER_{category_name}__"}
            })
            
            return True
            
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False
    
    def cleanup_category_placeholders(self, user_id: str) -> int:
        """Remove temporary category placeholder items"""
        try:
            result = self.menu_items_collection.delete_many({
                "user_id": user_id,
                "name": {"$regex": "__TEMP_CATEGORY_PLACEHOLDER_"}
            })
            return result.deleted_count
            
        except Exception as e:
            print(f"Error cleaning up placeholders: {e}")
            return 0

    # ========================================================================
    # TRANSACTION MANAGEMENT FUNCTIONS  
    # ========================================================================
    
    def create_transaction(self, user_id: str, items: List[Dict[str, Any]], total_amount: str, 
                          currency: str = "MYR", customer_name: Optional[str] = None, 
                          customer_id: Optional[str] = None, notes: Optional[str] = None, delivery_charge: float = 0.0) -> Optional[str]:
        """Record a new sales transaction"""
        try:
            # Validate required fields
            if not user_id or not items or not total_amount:
                raise ValidationException("user_id, items, and total_amount are required")
                
            # Convert user_id to ObjectId for consistency
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Build the transaction document to save in MongoDB
            transaction_doc = {
                "user_id": user_object_id,  # Which business recorded this sale (as ObjectId)
                "items": items,  # List of items sold (with quantities and prices)
                "total_amount": total_amount,  # Total sale amount as string
                "currency": currency,  # Currency used (from user's base_currency)
                "customer_name": customer_name,  # Optional customer name
                "customer_id": customer_id,  # Optional customer ID for CRM tracking
                "notes": notes,  # Optional transaction notes
                "delivery_charge": delivery_charge,  # Delivery/shipping charges
                "created_at": datetime.now(),  # When transaction was recorded
                "sale_date": datetime.now().strftime("%Y-%m-%d")  # Date of sale (for daily reports)
            }
            
            # Insert into MongoDB and get the new transaction's ID
            result = self.transactions_collection.insert_one(transaction_doc)
            transaction_id = str(result.inserted_id)
            
            # Update customer stats if customer_id provided
            if customer_id:
                self.update_customer_transaction_stats(customer_id, total_amount)
            
            return transaction_id  # Return the new transaction's ID as a string
            
        except ValidationException:
            raise  # Re-raise validation errors
        except Exception as e:
            raise DatabaseException(f"Failed to create transaction: {str(e)}")

    def get_user_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent transactions for a specific user/business (includes both sales and refunds)"""
        try:
            from datetime import datetime
            
            # Convert string user_id to ObjectId for database query
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Get all transactions for this user (query both string and ObjectId formats)
            # This handles legacy data where user_id might be stored in either format
            transactions = list(
                self.transactions_collection
                .find({"$or": [{"user_id": user_object_id}, {"user_id": user_id}]})
                .limit(limit * 2)  # Get more to account for sorting
            )
            
            # Add unified timestamp for sorting (handles both created_at and timestamp fields)
            for transaction in transactions:
                transaction["_id"] = str(transaction["_id"])  # Convert ObjectId to string
                
                # Create unified sort timestamp (prefer timestamp over created_at)
                if 'timestamp' in transaction:
                    transaction['sort_timestamp'] = transaction['timestamp']
                elif 'created_at' in transaction:
                    transaction['sort_timestamp'] = transaction['created_at']
                else:
                    # Fallback to ObjectId creation time
                    if ObjectId.is_valid(transaction["_id"]):
                        transaction['sort_timestamp'] = ObjectId(transaction["_id"]).generation_time
                    else:
                        transaction['sort_timestamp'] = datetime.now()
            
            # Sort by unified timestamp (newest first) and limit results
            transactions.sort(key=lambda x: x.get('sort_timestamp', datetime.min), reverse=True)
            transactions = transactions[:limit]
                
            return transactions  # Return list of transactions (empty list if none found)
            
        except Exception as e:
            print(f"Error getting user transactions: {e}")  # Log the error for debugging
            return []  # Return empty list if query failed

    def get_daily_sales_summary(self, user_id: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get sales summary for a specific date (default: today)"""
        try:
            # Use today's date if none provided
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Find all transactions for this user on this date
            transactions = list(
                self.transactions_collection.find({
                    "user_id": user_id,
                    "sale_date": date
                })
            )
            
            # Calculate summary statistics
            total_sales = len(transactions)
            total_amount = 0.0
            total_items = 0
            
            for transaction in transactions:
                # Add up the total amounts (convert string to float for calculation)
                total_amount += float(transaction["total_amount"])
                # Count total items sold
                for item in transaction["items"]:
                    total_items += item["quantity"]
            
            return {
                "date": date,
                "total_transactions": total_sales,
                "total_amount": f"{total_amount:.2f}",  # Convert back to string with 2 decimals
                "total_items_sold": total_items,
                "transactions": transactions
            }
            
        except Exception as e:
            print(f"Error getting daily sales summary: {e}")  # Log the error for debugging
            return {
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "total_transactions": 0,
                "total_amount": "0.00",
                "total_items_sold": 0,
                "transactions": []
            }

    # ========================================================================
    # CUSTOMER/MEMBER MANAGEMENT FUNCTIONS
    # ========================================================================

    def create_customer(self, user_id: str, name: str, phone: Optional[str] = None, 
                       email: Optional[str] = None, birthday: Optional[str] = None, notes: Optional[str] = None,
                       address: Optional[str] = None, customer_type: str = "Individual") -> Optional[str]:
        """Create a new customer/member record"""
        try:
            # Validate that at least phone or email is provided
            if not phone and not email:
                raise ValidationException("Either phone or email must be provided")
            
            if not user_id or not name:
                raise ValidationException("user_id and name are required")
            
            # Generate unique Customer ID for this business
            customer_id = self._generate_customer_id(user_id)
            
            customer_doc = {
                "user_id": user_id,  # Which business this customer belongs to
                "customer_id": customer_id,  # Unique Customer ID (e.g., CUST-001, CUST-002)
                "name": name,
                "phone": phone,
                "email": email,
                "address": address,
                "customer_type": customer_type,  # Business or Individual
                "birthday": birthday,
                "notes": notes,
                "is_active": True,
                "total_visits": 0,
                "total_spent": "0.00",
                "last_visit": None,
                "sms_marketing": True,  # Default opt-in for SMS
                "email_marketing": True,  # Default opt-in for email
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result = self.customers_collection.insert_one(customer_doc)
            return str(result.inserted_id)
            
        except ValidationException:
            raise  # Re-raise validation errors
        except Exception as e:
            raise DatabaseException(f"Failed to create customer: {str(e)}")
    
    def _generate_customer_id(self, user_id: str) -> str:
        """Generate unique Customer ID for a business (e.g., CUST-001, CUST-002)"""
        try:
            # Convert string user_id to ObjectId if valid
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Count existing customers for this business
            customer_count = self.customers_collection.count_documents({"user_id": user_object_id})
            
            # Generate next customer ID (starting from 001)
            next_number = customer_count + 1
            customer_id = f"CUST-{next_number:03d}"
            
            # Check if this ID already exists (in case of race conditions)
            while self.customers_collection.find_one({"user_id": user_object_id, "customer_id": customer_id}):
                next_number += 1
                customer_id = f"CUST-{next_number:03d}"
            
            return customer_id
            
        except Exception as e:
            print(f"Error generating customer ID: {e}")
            # Fallback to timestamp-based ID
            import time
            return f"CUST-{int(time.time())}"

    def search_customers(self, user_id: str, search_term: str = None):
        """Search customers by name, phone, or email"""
        try:
            # Convert string user_id to ObjectId if valid
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Base query that handles both string and ObjectId user_id formats
            # Also handles customers with missing is_active field (treats as active)
            base_query = {
                "$or": [{"user_id": user_object_id}, {"user_id": user_id}],
                "$or": [
                    {"is_active": True},
                    {"is_active": {"$exists": False}}  # Include customers without is_active field
                ]
            }
            
            if search_term:
                # Search in name, phone, or email (case-insensitive)
                search_regex = {"$regex": search_term, "$options": "i"}
                # Combine user_id query with search query
                query = {
                    "$and": [
                        {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]},
                        {
                            "$or": [
                                {"is_active": True},
                                {"is_active": {"$exists": False}}
                            ]
                        },
                        {
                            "$or": [
                                {"name": search_regex},
                                {"phone": search_regex},
                                {"email": search_regex}
                            ]
                        }
                    ]
                }
            else:
                query = {
                    "$and": [
                        {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]},
                        {
                            "$or": [
                                {"is_active": True},
                                {"is_active": {"$exists": False}}
                            ]
                        }
                    ]
                }
            
            customers = list(
                self.customers_collection
                .find(query)
                .sort("name", 1)  # Sort alphabetically by name
                .limit(100)  # Increased limit to show all customers
            )
            
            # Convert ObjectId to string and format for display
            for customer in customers:
                customer["_id"] = str(customer["_id"])
            
            return customers
            
        except Exception as e:
            print(f"Error searching customers: {e}")
            return []

    def get_customer_by_contact(self, user_id: str, phone: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find customer by phone or email"""
        try:
            # Use the query builder helper
            query = self._build_customer_search_query(user_id, phone, email)
            
            customer = self.customers_collection.find_one(query)
            if customer:
                customer["_id"] = str(customer["_id"])
            
            return customer
            
        except ValidationException:
            raise  # Re-raise validation errors
        except Exception as e:
            raise DatabaseException(f"Error finding customer: {str(e)}")

    def update_customer_transaction_stats(self, customer_id: str, transaction_amount: str) -> bool:
        """Update customer's visit count and total spent after a transaction"""
        try:
            current_total = self.customers_collection.find_one({"_id": ObjectId(customer_id)})
            if current_total:
                new_total = float(current_total.get("total_spent", "0.00")) + float(transaction_amount)
                new_visits = current_total.get("total_visits", 0) + 1
                
                self.customers_collection.update_one(
                    {"_id": ObjectId(customer_id)},
                    {
                        "$set": {
                            "total_visits": new_visits,
                            "total_spent": f"{new_total:.2f}",
                            "last_visit": datetime.now().strftime("%Y-%m-%d"),
                            "updated_at": datetime.now()
                        }
                    }
                )
                return True
            return False
            
        except Exception as e:
            print(f"Error updating customer stats: {e}")
            return False

    def get_customers_for_marketing(self, user_id: str, marketing_type: str = "both") -> List[Dict[str, Any]]:
        """Get customers opted in for marketing (SMS or Email)"""
        try:
            # Use helpers for common query patterns
            user_query_or = self._build_user_id_query(user_id)
            active_query = self._build_active_filter()
            
            if marketing_type == "sms":
                query = {
                    "$and": [
                        user_query_or,
                        active_query,
                        {"sms_marketing": True},
                        {"phone": {"$ne": None}}
                    ]
                }
            elif marketing_type == "email":
                query = {
                    "$and": [
                        user_query_or,
                        active_query,
                        {"email_marketing": True},
                        {"email": {"$ne": None}}
                    ]
                }
            else:  # both
                query = {
                    "$and": [
                        user_query_or,
                        active_query,
                        {
                            "$or": [
                                {"sms_marketing": True, "phone": {"$ne": None}},
                                {"email_marketing": True, "email": {"$ne": None}}
                            ]
                        }
                    ]
                }
            
            customers = list(self.customers_collection.find(query))
            
            # Convert ObjectId to string
            for customer in customers:
                customer["_id"] = str(customer["_id"])
            
            return customers
            
        except Exception as e:
            raise DatabaseException(f"Error fetching marketing customers: {str(e)}")

    def sync_customers_from_transactions(self, user_id: str):
        """Automatically sync customers from transaction data"""
        try:
            # Convert string user_id to ObjectId
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Get all transactions for this user (query both string and ObjectId formats)
            transactions = list(self.transactions_collection.find(
                {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]}
            ))
            
            # Extract unique customer names (excluding Walk-in, None, empty)
            customer_names = set()
            customer_stats = {}  # Track visits and spending per customer
            
            for transaction in transactions:
                customer_name = transaction.get('customer_name') or ''
                customer_name = customer_name.strip() if customer_name else ''
                
                # Skip if no name, Walk-in, Anonymous, or empty
                if not customer_name or customer_name.lower() in ['walk-in', 'anonymous', 'none', '']:
                    continue
                
                customer_names.add(customer_name)
                
                # Track stats
                if customer_name not in customer_stats:
                    customer_stats[customer_name] = {
                        'total_visits': 0,
                        'total_spent': 0.0,
                        'first_visit': transaction.get('created_at', datetime.now()),
                        'last_visit': transaction.get('created_at', datetime.now())
                    }
                
                customer_stats[customer_name]['total_visits'] += 1
                customer_stats[customer_name]['total_spent'] += float(transaction.get('total_amount', 0))
                
                # Update visit dates
                transaction_date = transaction.get('created_at', datetime.now())
                if transaction_date < customer_stats[customer_name]['first_visit']:
                    customer_stats[customer_name]['first_visit'] = transaction_date
                if transaction_date > customer_stats[customer_name]['last_visit']:
                    customer_stats[customer_name]['last_visit'] = transaction_date
            
            # Check which customers don't exist in customer collection yet
            existing_customers = list(self.customers_collection.find(
                {"user_id": user_object_id}, 
                {"name": 1}
            ))
            existing_names = {customer['name'] for customer in existing_customers}
            
            # Add missing customers
            new_customers_added = 0
            for customer_name in customer_names:
                if customer_name not in existing_names:
                    # Generate hypothetical contact details for demo purposes
                    demo_email = self._generate_demo_email(customer_name)
                    demo_phone = self._generate_demo_phone()
                    
                    # Create new customer record
                    new_customer = {
                        "user_id": user_object_id,
                        "name": customer_name,
                        "phone": demo_phone,
                        "email": demo_email,
                        "total_visits": customer_stats[customer_name]['total_visits'],
                        "total_spent": round(customer_stats[customer_name]['total_spent'], 2),
                        "marketing_consent": False,  # Default to no consent
                        "sms_marketing": False,
                        "email_marketing": False,
                        "notes": "Demo customer - Auto-generated contact details",
                        "is_active": True,
                        "created_at": customer_stats[customer_name]['first_visit'],
                        "last_visit": customer_stats[customer_name]['last_visit']
                    }
                    
                    self.customers_collection.insert_one(new_customer)
                    new_customers_added += 1
                else:
                    # Update existing customer stats
                    self.customers_collection.update_one(
                        {"user_id": user_object_id, "name": customer_name},
                        {
                            "$set": {
                                "total_visits": customer_stats[customer_name]['total_visits'],
                                "total_spent": round(customer_stats[customer_name]['total_spent'], 2),
                                "last_visit": customer_stats[customer_name]['last_visit']
                            }
                        }
                    )
            
            return new_customers_added
            
        except Exception as e:
            print(f"Error syncing customers from transactions: {e}")
            return 0

    # ========================================================================
    # BUSINESS SETTINGS MANAGEMENT FUNCTIONS
    # ========================================================================

    def update_business_info(self, user_id: str, business_name: str = None, 
                            business_address: str = None, tax_id: str = None,
                            base_currency: str = None):
        """Update business information"""
        try:
            update_doc = {"updated_at": datetime.now()}
            
            if business_name:
                update_doc["business_name"] = business_name
            if business_address is not None:  # Allow empty string
                update_doc["business_address"] = business_address
            if tax_id is not None:  # Allow empty string
                update_doc["tax_id"] = tax_id
            if base_currency:
                update_doc["base_currency"] = base_currency
            
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_doc}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating business info: {e}")
            return False

    def update_business_pin(self, user_id: str, new_pin: str):
        """Update business PIN with proper hashing"""
        try:
            # Hash the new PIN
            pin_hash = bcrypt.hashpw(new_pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "pin_hash": pin_hash,
                    "updated_at": datetime.now()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating PIN: {e}")
            return False

    def get_business_info(self, user_id: str):
        """Get complete business information"""
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return user
            
        except Exception as e:
            print(f"Error getting business info: {e}")
            return None

    def export_all_data(self, user_id: str):
        """Export all business data for backup"""
        try:
            # Get all business data
            business_info = self.get_business_info(user_id)
            menu_items = self.get_user_menu_items(user_id)
            transactions = self.get_user_transactions(user_id, limit=1000)  # Get more for export
            customers = self.search_customers(user_id)
            
            export_data = {
                "business_info": business_info,
                "menu_items": menu_items,
                "transactions": transactions,
                "customers": customers,
                "export_timestamp": datetime.now().isoformat(),
                "total_menu_items": len(menu_items),
                "total_transactions": len(transactions),
                "total_customers": len(customers)
            }
            
            return export_data
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a single user by ID"""
        try:
            # Convert string user_id to ObjectId if it's a valid ObjectId
            user_object_id = self._ensure_object_id(user_id)

            user = self.users_collection.find_one({"_id": user_object_id})
            if user:
                user["_id"] = str(user["_id"])
                return user
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    def update_user(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None, age: Optional[int] = None) -> bool:
        """Update a user"""
        try:
            # Convert string user_id to ObjectId if it's a valid ObjectId
            user_object_id = self._ensure_object_id(user_id)

            # Build update data (only include non-None fields)
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if email is not None:
                update_data["email"] = email
            if age is not None:
                update_data["age"] = age
            
            if not update_data:
                return False
            
            result = self.users_collection.update_one(
                {"_id": user_object_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def update_user_theme(self, user_id: str, theme_name: str) -> bool:
        """Update user's preferred theme"""
        try:
            # Convert string user_id to ObjectId if it's a valid ObjectId
            user_object_id = self._ensure_object_id(user_id)

            result = self.users_collection.update_one(
                {"_id": user_object_id},
                {"$set": {"preferred_theme": theme_name, "updated_at": datetime.now().isoformat()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user theme: {e}")
            return False

    def get_user_theme(self, user_id: str) -> str:
        """Get user's preferred theme"""
        try:
            # Convert string user_id to ObjectId if it's a valid ObjectId
            user_object_id = self._ensure_object_id(user_id)

            user = self.users_collection.find_one({"_id": user_object_id}, {"preferred_theme": 1})
            if user and "preferred_theme" in user:
                return user["preferred_theme"]
            return "Default"  # Return default theme if not set
        except Exception as e:
            print(f"Error fetching user theme: {e}")
            return "Default"

# Close DB Function:
    def close(self) -> None:
        """Close the MongoDB connection"""
        self.client.close()
    
    # Helper functions for generating demo contact details
    def _generate_demo_email(self, name: str) -> str:
        """Generate a hypothetical email for demo purposes"""
        import random
        name_parts = name.lower().replace(' ', '.').replace("'", "").replace("-", "")
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'example.com']
        return f"{name_parts}@{random.choice(domains)}"
    
    def _generate_demo_phone(self) -> str:
        """Generate a Malaysian phone number for demo purposes"""
        import random
        prefixes = ['012', '013', '014', '016', '017', '018', '019']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"+6{prefix}{suffix}"

    # Account Recovery Methods
    def update_recovery_contact(self, user_id: str, email: str = None, phone: str = None):
        """Update user's recovery contact information"""
        try:
            update_data = {"updated_at": datetime.now()}
            if email:
                update_data["recovery_email"] = email
            if phone:
                update_data["recovery_phone"] = phone
            
            result = self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating recovery contact: {e}")
            return False
    
    def find_business_by_recovery_contact(self, email: str = None, phone: str = None):
        """Find business name using recovery email or phone"""
        try:
            query = {}
            if email:
                query["recovery_email"] = email
            elif phone:
                query["recovery_phone"] = phone
            else:
                return None
            
            user = self.users_collection.find_one(query)
            if user:
                return {
                    "business_name": user.get("business_name"),
                    "user_id": str(user["_id"]),
                    "business_type": user.get("business_type")
                }
            return None
        except Exception as e:
            print(f"Error finding business: {e}")
            return None
    
    def verify_recovery_and_reset_pin(self, business_name: str, recovery_contact: str, new_pin: str):
        """Verify recovery contact and reset PIN"""
        try:
            # Find user by business name and verify recovery contact
            user = self.users_collection.find_one({
                "business_name": business_name,
                "$or": [
                    {"recovery_email": recovery_contact},
                    {"recovery_phone": recovery_contact}
                ]
            })
            
            if not user:
                return False
            
            # Hash new PIN and update
            pin_hash = bcrypt.hashpw(new_pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            result = self.users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"pin_hash": pin_hash, "updated_at": datetime.now()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error resetting PIN: {e}")
            return False
    
    # ==================== QUOTATION MANAGEMENT METHODS ====================
    
    def create_quotation(self, user_id: str, customer_id: str, customer_name: str, line_items: List[Dict[str, Any]], 
                        subtotal: Union[str, float], tax_amount: Union[str, float], total_amount: Union[str, float], validity_days: int = 30, 
                        payment_terms: Optional[str] = None, notes: Optional[str] = None, status: str = "Draft", delivery_charge: float = 0.0) -> Optional[str]:
        """
        Create a new quotation
        
        Args:
            user_id: Business user ID
            customer_id: Customer ID
            customer_name: Customer name
            line_items: List of items [{offering_id, offering_name, quantity, unit_price, total_price}]
            subtotal: Subtotal before tax
            tax_amount: Tax amount
            total_amount: Final total
            validity_days: Valid for X days (default 30)
            payment_terms: Payment terms text
            notes: Additional notes
            status: Quotation status (Draft, Sent, Accepted, Rejected, Expired)
            delivery_charge: Delivery/shipping charges
        
        Returns:
            quotation_id if successful, None otherwise
        """
        try:
            # Generate quotation number
            quotation_number = self.generate_quotation_number(user_id)
            
            # Calculate validity date
            from datetime import datetime, timedelta
            valid_until = (datetime.now() + timedelta(days=validity_days)).strftime("%Y-%m-%d")
            
            quotation = {
                "user_id": user_id,
                "quotation_number": quotation_number,
                "customer_id": customer_id,
                "customer_name": customer_name,
                "line_items": line_items,
                "subtotal": float(subtotal),
                "tax_amount": float(tax_amount),
                "delivery_charge": float(delivery_charge),
                "total_amount": float(total_amount),
                "validity_days": validity_days,
                "valid_until": valid_until,
                "payment_terms": payment_terms,
                "notes": notes,
                "status": status,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "converted_to_sale": False,
                "transaction_id": None
            }
            
            result = self.quotations_collection.insert_one(quotation)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating quotation: {e}")
            return None
    
    def generate_quotation_number(self, user_id: str) -> str:
        """
        Generate auto-incremented quotation number
        Format: QT-2025-001, QT-2025-002, etc.
        """
        try:
            from datetime import datetime
            year = datetime.now().year
            
            # Count existing quotations for this user in this year
            count = self.quotations_collection.count_documents({
                "user_id": user_id,
                "created_at": {
                    "$gte": datetime(year, 1, 1),
                    "$lt": datetime(year + 1, 1, 1)
                }
            })
            
            quotation_number = f"QT-{year}-{str(count + 1).zfill(3)}"
            return quotation_number
            
        except Exception as e:
            print(f"Error generating quotation number: {e}")
            return f"QT-{year}-001"
    
    def get_user_quotations(self, user_id: str, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get quotations for a user, optionally filtered by status"""
        try:
            # Convert string user_id to ObjectId if valid
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Query both string and ObjectId formats for user_id
            query = {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]}
            
            if status:
                # Combine user_id query with status filter
                query = {
                    "$and": [
                        {"$or": [{"user_id": user_object_id}, {"user_id": user_id}]},
                        {"status": status}
                    ]
                }
            
            quotations = list(self.quotations_collection.find(query)
                            .sort("created_at", -1)
                            .limit(limit))
            return quotations
        except Exception as e:
            print(f"Error getting quotations: {e}")
            return []
    
    def get_quotation_by_id(self, quotation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific quotation by ID"""
        try:
            return self.quotations_collection.find_one({"_id": ObjectId(quotation_id)})
        except Exception as e:
            print(f"Error getting quotation: {e}")
            return None
    
    def get_quotation_by_number(self, user_id: str, quotation_number: str) -> Optional[Dict[str, Any]]:
        """Get a quotation by its quotation number"""
        try:
            # Convert string user_id to ObjectId if valid
            user_object_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
            
            # Query both string and ObjectId formats for user_id
            return self.quotations_collection.find_one({
                "$or": [{"user_id": user_object_id}, {"user_id": user_id}],
                "quotation_number": quotation_number
            })
        except Exception as e:
            print(f"Error getting quotation by number: {e}")
            return None
    
    def update_quotation(self, quotation_id, line_items=None, subtotal=None, 
                        tax_amount=None, total_amount=None, payment_terms=None, 
                        notes=None, status=None, validity_days=None, valid_until=None):
        """Update an existing quotation"""
        try:
            from datetime import datetime
            update_fields = {"updated_at": datetime.now()}
            
            if line_items is not None:
                update_fields["line_items"] = line_items
            if subtotal is not None:
                update_fields["subtotal"] = float(subtotal)
            if tax_amount is not None:
                update_fields["tax_amount"] = float(tax_amount)
            if total_amount is not None:
                update_fields["total_amount"] = float(total_amount)
            if payment_terms is not None:
                update_fields["payment_terms"] = payment_terms
            if notes is not None:
                update_fields["notes"] = notes
            if status is not None:
                update_fields["status"] = status
            if validity_days is not None:
                update_fields["validity_days"] = validity_days
            if valid_until is not None:
                update_fields["valid_until"] = valid_until
            
            result = self.quotations_collection.update_one(
                {"_id": ObjectId(quotation_id)},
                {"$set": update_fields}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating quotation: {e}")
            return False
    
    def update_quotation_status(self, quotation_id, status, transaction_id=None):
        """Update quotation status and optionally link to transaction"""
        try:
            from datetime import datetime
            update_fields = {
                "status": status,
                "updated_at": datetime.now()
            }
            
            if status == "Accepted" and transaction_id:
                update_fields["converted_to_sale"] = True
                update_fields["transaction_id"] = transaction_id
            
            result = self.quotations_collection.update_one(
                {"_id": ObjectId(quotation_id)},
                {"$set": update_fields}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating quotation status: {e}")
            return False
    
    def delete_quotation(self, quotation_id):
        """Delete a quotation"""
        try:
            result = self.quotations_collection.delete_one({"_id": ObjectId(quotation_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting quotation: {e}")
            return False
    
    def mark_quotation_as_converted(self, quotation_id, transaction_id):
        """Mark a quotation as converted to sale"""
        try:
            from datetime import datetime
            update_fields = {
                "status": "Converted",
                "converted_to_sale": True,
                "transaction_id": str(transaction_id),
                "converted_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result = self.quotations_collection.update_one(
                {"_id": ObjectId(quotation_id)},
                {"$set": update_fields}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error marking quotation as converted: {e}")
            return False
    
    # ==================== DOCUMENT MANAGEMENT METHODS ====================
    
    def create_document(self, user_id, doc_type, customer_id=None, customer_name=None, 
                       line_items=None, subtotal=0, tax_amount=0, total_amount=0,
                       validity_days=None, due_date=None, payment_status=None,
                       delivery_address=None, delivery_date=None, notes=None, **kwargs):
        """
        Create a new document (quotation, invoice, receipt, or delivery order)
        
        Args:
            user_id: Business user ID
            doc_type: 'quotation', 'invoice', 'receipt', or 'delivery_order'
            customer_id: Customer ID (if applicable)
            customer_name: Customer name
            line_items: List of items [{offering_id, offering_name, quantity, unit_price, total_price}]
            subtotal: Subtotal before tax
            tax_amount: Tax amount
            total_amount: Final total
            validity_days: For quotations - valid for X days
            due_date: For invoices - payment due date
            payment_status: For invoices - 'pending', 'paid', 'overdue'
            delivery_address: For delivery orders
            delivery_date: For delivery orders
            notes: Additional notes
            **kwargs: Additional fields (terms_conditions, transaction_id, etc.)
        
        Returns:
            document_id if successful, None otherwise
        """
        try:
            # Generate document number
            doc_number = self.generate_document_number(user_id, doc_type)
            
            document = {
                "user_id": user_id,
                "document_type": doc_type,
                "document_number": doc_number,
                "customer_id": customer_id,
                "customer_name": customer_name or "Walk-in",
                "line_items": line_items or [],
                "subtotal": float(subtotal),
                "tax_amount": float(tax_amount),
                "total_amount": float(total_amount),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "notes": notes
            }
            
            # Add type-specific fields
            if doc_type == "quotation":
                document["validity_days"] = validity_days or 30
                document["valid_until"] = (datetime.now() + timedelta(days=validity_days or 30)).strftime("%Y-%m-%d")
                document["status"] = kwargs.get("status", "draft")  # draft, sent, accepted, rejected, expired
                document["terms_conditions"] = kwargs.get("terms_conditions")
                
            elif doc_type == "invoice":
                document["due_date"] = due_date
                document["payment_status"] = payment_status or "pending"  # pending, paid, partial, overdue
                document["payment_method"] = kwargs.get("payment_method")
                document["quotation_id"] = kwargs.get("quotation_id")  # Link to quotation if converted
                document["transaction_id"] = kwargs.get("transaction_id")  # Link to transaction when paid
                document["amount_paid"] = kwargs.get("amount_paid", 0)
                document["balance_due"] = float(total_amount) - float(kwargs.get("amount_paid", 0))
                
            elif doc_type == "receipt":
                document["transaction_id"] = kwargs.get("transaction_id")  # Link to original transaction
                document["payment_method"] = kwargs.get("payment_method")
                document["receipt_type"] = kwargs.get("receipt_type", "sale")  # sale, refund, payment
                
            elif doc_type == "delivery_order":
                document["delivery_address"] = delivery_address
                document["delivery_date"] = delivery_date
                document["delivery_status"] = kwargs.get("delivery_status", "pending")  # pending, in_transit, delivered, cancelled
                document["tracking_number"] = kwargs.get("tracking_number")
                document["driver_name"] = kwargs.get("driver_name")
                document["driver_contact"] = kwargs.get("driver_contact")
                document["invoice_id"] = kwargs.get("invoice_id")  # Link to invoice
                document["signature_image"] = kwargs.get("signature_image")  # Base64 encoded signature
                document["delivered_at"] = kwargs.get("delivered_at")
            
            result = self.documents_collection.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating document: {e}")
            return None
    
    def generate_document_number(self, user_id, doc_type):
        """
        Generate auto-incremented document number
        Format: QT-2025-001, INV-2025-001, OR-2025-001, DO-2025-001
        """
        try:
            # Get prefix based on document type
            prefixes = {
                "quotation": "QT",
                "invoice": "INV",
                "receipt": "OR",  # Official Receipt
                "delivery_order": "DO"
            }
            prefix = prefixes.get(doc_type, "DOC")
            
            # Get current year
            year = datetime.now().year
            
            # Count existing documents of this type for this user in this year
            count = self.documents_collection.count_documents({
                "user_id": user_id,
                "document_type": doc_type,
                "created_at": {
                    "$gte": datetime(year, 1, 1),
                    "$lt": datetime(year + 1, 1, 1)
                }
            })
            
            # Generate number: PREFIX-YEAR-SEQUENCE
            doc_number = f"{prefix}-{year}-{str(count + 1).zfill(3)}"
            return doc_number
            
        except Exception as e:
            print(f"Error generating document number: {e}")
            return f"{prefix}-{year}-001"
    
    def get_user_documents(self, user_id, doc_type=None, limit=100):
        """Get documents for a user, optionally filtered by type"""
        try:
            query = {"user_id": user_id}
            if doc_type:
                query["document_type"] = doc_type
            
            documents = list(self.documents_collection.find(query)
                           .sort("created_at", -1)
                           .limit(limit))
            return documents
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def get_document_by_id(self, document_id):
        """Get a specific document by ID"""
        try:
            return self.documents_collection.find_one({"_id": ObjectId(document_id)})
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    def get_document_by_number(self, user_id, document_number):
        """Get a document by its document number"""
        try:
            return self.documents_collection.find_one({
                "user_id": user_id,
                "document_number": document_number
            })
        except Exception as e:
            print(f"Error getting document by number: {e}")
            return None
    
    def update_document_status(self, document_id, status, **kwargs):
        """Update document status and related fields"""
        try:
            update_fields = {
                "status": status,
                "updated_at": datetime.now()
            }
            
            # Add any additional fields passed in kwargs
            update_fields.update(kwargs)
            
            result = self.documents_collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_fields}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating document status: {e}")
            return False
    
    def delete_document(self, document_id):
        """Delete a document"""
        try:
            result = self.documents_collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
