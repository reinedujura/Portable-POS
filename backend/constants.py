"""Application Constants"""

# Database
DB_NAME = "portable_pos_db"

# Collections
COLLECTION_TRANSACTIONS = "transactions"
COLLECTION_CUSTOMERS = "customers"
COLLECTION_USERS = "users"
COLLECTION_MENUS = "menu_items"
COLLECTION_QUOTATIONS = "quotations"
COLLECTION_DOCUMENTS = "documents"

# User Roles
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_CASHIER = "cashier"

# Business Types
BUSINESS_TYPE_STREET_VENDOR = "street_vendor"
BUSINESS_TYPE_TUTOR = "tutor"
BUSINESS_TYPE_YOGA = "yoga_teacher"
BUSINESS_TYPE_CONSULTANT = "consultant"
BUSINESS_TYPE_RETAIL = "retail"
BUSINESS_TYPE_SERVICE = "service"

# Transaction Status
STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"

# Payment Methods
PAYMENT_CASH = "cash"
PAYMENT_CARD = "card"
PAYMENT_CHECK = "check"
PAYMENT_MOBILE = "mobile"

# Validation Constraints
MIN_CUSTOMER_NAME_LENGTH = 2
MAX_CUSTOMER_NAME_LENGTH = 100
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 100
MAX_TRANSACTION_ITEMS = 1000
MIN_BUSINESS_NAME_LENGTH = 2

# Error Messages
ERROR_INVALID_EMAIL = "Invalid email format"
ERROR_DUPLICATE_EMAIL = "Email already exists"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_CUSTOMER_NOT_FOUND = "Customer not found"
ERROR_TRANSACTION_NOT_FOUND = "Transaction not found"
ERROR_INSUFFICIENT_PERMISSIONS = "Insufficient permissions"

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# Currencies
CURRENCY_MYR = "MYR"
CURRENCY_SGD = "SGD"
CURRENCY_USD = "USD"
CURRENCY_THB = "THB"

# Date Formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
