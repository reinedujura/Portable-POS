# Portable POS - Complete User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Main Dashboard](#main-dashboard)
5. [Features & Functions](#features--functions)
6. [Tips & Tricks](#tips--tricks)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

**Portable POS** is a professional Point-of-Sale (POS) system designed for small to medium businesses. It provides real-time sales tracking, customer management, inventory control, and AI-powered business insights - all accessible from your local network.

### Key Features
- 📊 Real-time sales analytics and reporting
- 👥 Complete customer management system
- 💳 Transaction tracking and refund management
- 📦 Inventory and menu management
- 🤖 AI-powered insights (sales forecasting, customer analysis, marketing recommendations)
- 📱 Mobile-friendly interface (accessible on phones via WiFi)
- 🔐 Secure PIN-based authentication
- 📄 Multiple export formats (Excel, PDF, CSV)

---

## Getting Started

### System Requirements
- Python 3.7+ installed
- MongoDB Atlas account (cloud database)
- Google Gemini API key (for AI features)
- Internet connection for initial setup

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/reinedujura/Portable-POS.git
   cd Portable-POS
   ```

2. **Set up Python virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # or
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   Copy your MongoDB URI and Google Gemini API key into a `.env` file:
   
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/portable_pos_db
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run frontend/app.py --server.address=0.0.0.0
   ```

6. **Access the app:**
   - **Desktop:** `https://localhost:8502`
   - **Mobile (same WiFi):** `https://192.168.1.4:8502` (or your local IP)

---

## Authentication

### First-Time Setup: Register Your Business

When you first access the app, you'll see the **Register** page.

**Steps:**
1. Enter your **Business Name** (e.g., "John's Bakery")
2. Create a **PIN** (4-6 digits for quick login)
3. Confirm your PIN
4. Click **Register**

Your business will be created in the database, and you'll be automatically logged in.

### Login

**Every time you restart the app:**
1. Enter your **Business Name**
2. Enter your **PIN**
3. Click **Login**

**Forgot your PIN?**
- Click "Forgot PIN?" → Enter your business name → Reset with new PIN

**Forgot your business name?**
- Click "Forgot Business Name?" → Enter your email (if registered) → Recover your business name

---

## Main Dashboard

Once logged in, you'll see the **main dashboard** with 7 tabs:

### Tab 1: 📊 Sales & Analytics
Track all your sales transactions and view detailed analytics.

**Features:**
- **View Sales:** See all transactions with date, amount, items sold, payment method
- **New Sale:** Create a new transaction
- **Sales Report:** Generate PDF/Excel reports for date ranges
- **Refunds:** Process refunds for previous sales
- **Visual Dashboard:** Charts showing sales trends
- **Metrics:** Key performance indicators (total sales, average transaction, daily revenue)
- **AI Analytics:** Forecasting and insights

**How to Create a Sale:**
1. Go to **Sales & Analytics** tab
2. Click **💳 New Sale**
3. Select items from the menu (quantity + item)
4. Enter customer details (optional)
5. Choose payment method (Cash, Card, Mobile Money, Other)
6. Click **Complete Sale**
7. Download receipt (PDF/CSV/Text)

### Tab 2: 👥 Customers
Manage your customer database.

**Features:**
- **View Customers:** See all customers, their purchase history, total spent
- **Add Customer:** Register new customers with contact info
- **Customer Details:** View individual customer profiles and transaction history
- **Customer Reports:** Generate customer lists and reports

**How to Add a Customer:**
1. Go to **Customers** tab
2. Click **➕ Add Customer**
3. Fill in details:
   - Name
   - Email
   - Phone
   - Address
4. Click **Save Customer**

### Tab 3: 📦 Inventory
Manage your products and menu items.

**Features:**
- **View Menu:** See all available menu items and categories
- **Menu Management:** Add, edit, delete menu items
- **Categories:** Organize items into categories (Food, Drinks, etc.)
- **Stock Levels:** Track quantity available
- **Pricing:** Set and update prices

**How to Add a Menu Item:**
1. Go to **Inventory** tab
2. Click **⚙️ Menu Management**
3. Click **➕ Create** under Category (Food, Drinks, etc.)
4. Fill in:
   - Item Name (e.g., "Cappuccino")
   - Description
   - Price
   - Quantity in stock
5. Click **Save Item**

### Tab 4: 📝 Quotes & Invoices
Create professional quotes for customers.

**Features:**
- **New Quotation:** Create quote with items and pricing
- **View Quotes:** See all quotes and their status
- **Quotation Reports:** Export quotes as PDF

### Tab 5: 📊 Reports
Generate comprehensive business reports.

**Features:**
- **Sales Report:** Daily, weekly, monthly sales summaries
- **Customer Report:** Customer lists and spending analysis
- **Export Formats:** Excel, PDF, CSV
- **Date Range Filtering:** Choose specific periods

**How to Generate a Report:**
1. Go to **Reports** tab
2. Select **Report Type** (Sales, Customers, etc.)
3. Choose **Date Range**
4. Click **Generate Report**
5. Download as Excel/PDF

### Tab 6: 🤖 AI Analytics
Get intelligent business insights powered by Google Gemini AI.

**Features:**

**Sales Forecasting:**
- Predicts future sales trends
- Helps with inventory planning
- Identifies seasonal patterns

**Customer Insights:**
- Analysis of customer behavior
- Buying patterns and preferences
- Retention recommendations

**Menu Optimization:**
- Best-selling items analysis
- Profit margin analysis
- Product recommendations

**Marketing Insights:**
- Campaign recommendations
- Customer segmentation suggestions
- Promotional strategies

**Anomaly Detection:**
- Detects unusual transaction patterns
- Alerts for potential fraud
- Identifies data inconsistencies

**How to Use AI Features:**
1. Go to **🤖 AI Analytics** tab
2. Select the analysis type (e.g., "📈 Sales Forecast")
3. Click **Generate Analysis**
4. Read detailed AI-generated insights
5. Use recommendations for business decisions

### Tab 7: ⚙️ Settings
Configure your app preferences.

**Sub-tabs:**
- **General Settings:** Business name, email, timezone
- **Theme:** Light/Dark mode toggle
- **Data Export:** Export all your data
- **Backup:** Create database backups
- **Account:** View account information

---

## Features & Functions

### Sales Management

**Create a Sale:**
- Quick-add items from menu
- Specify quantities
- Add customer information (optional)
- Select payment method
- Generate receipt

**Process a Refund:**
1. Go to **Sales & Analytics** → **💰 Refunds**
2. Find the original transaction
3. Enter refund amount (full or partial)
4. Confirm refund
5. Receipt will be generated

**View Transaction Details:**
- Click on any transaction to see:
  - Items purchased
  - Quantities
  - Prices
  - Customer info
  - Payment method
  - Timestamp

### Receipts

Receipts are available in three formats:

**Text Receipt:**
- Simple text format
- Print-friendly
- Shows all transaction details

**CSV Receipt:**
- Comma-separated values
- Import into spreadsheets
- Useful for accounting

**PDF Receipt:**
- Professional formatted receipt
- Shows business logo/name
- Print-ready format

### Reports

**Sales Report:**
- Date range selection
- Transaction summary
- Total revenue
- Payment method breakdown
- PDF/Excel export

**Customer Report:**
- Customer list with contact info
- Total purchases per customer
- Average transaction value
- Contact details export

### Data Export

**Export Options:**
- **Excel:** Full formatted spreadsheets with charts
- **PDF:** Professional PDF reports
- **CSV:** Raw data for external processing

**Exported Data Includes:**
- Transactions
- Customers
- Products
- Financial summaries

---

## Tips & Tricks

### 1. Mobile Access
- Access the app on your phone while connected to WiFi
- Use the URL: `https://192.168.1.4:8502` (or your local IP)
- Bookmark for quick access

### 2. Fast Sales Entry
- Pre-enter customer details to speed up transactions
- Use keyboard shortcuts (if available) in menus
- Batch similar items together

### 3. AI Insights
- Check AI forecasting regularly for inventory planning
- Review customer insights monthly for marketing campaigns
- Use anomaly detection alerts to catch errors early

### 4. Backup Your Data
- Export reports regularly
- Use the backup feature weekly
- Keep copies of important reports

### 5. Theme Switching
- Use Light mode during day, Dark mode at night (less eye strain)
- Customize colors in Settings

### 6. Receipt Management
- PDF receipts for customers
- CSV for accounting records
- Keep digital copies for audit trails

---

## Troubleshooting

### Issue: "Cannot connect to MongoDB"
**Solution:**
- Check your `.env` file has correct MongoDB URI
- Ensure your IP is whitelisted in MongoDB Atlas
- Verify internet connection

### Issue: "AI features not working"
**Solution:**
- Check Google Gemini API key in `.env`
- Verify API key has sufficient quota
- Enable Google Generative AI API in your Google Cloud console

### Issue: "App won't load on mobile"
**Solution:**
- Ensure mobile is on same WiFi as the computer
- Use correct IP address (not localhost)
- Check firewall settings allow local network access
- Restart Streamlit if issues persist

### Issue: "PIN login not working"
**Solution:**
- Ensure you're entering correct business name
- PIN is case-sensitive
- Try "Forgot PIN?" to reset
- Check database connection

### Issue: "Can't export reports"
**Solution:**
- Check if Excel/openpyxl is installed
- Try different export format (PDF instead)
- Ensure sufficient disk space
- Restart the app

### Issue: "Transactions not saving"
**Solution:**
- Check MongoDB connection
- Verify internet connection
- Look for error messages in console
- Restart the application

### Issue: "Slow performance"
**Solution:**
- Clear browser cache
- Restart the Streamlit app
- Check internet connection speed
- Reduce date range for reports

---

## Visual Guide - Screenshots & Descriptions

### Screen 1: Login Page
```
┌─────────────────────────────────┐
│    🔐 Portable POS Login        │
├─────────────────────────────────┤
│                                 │
│  Business Name: [_____________] │
│  PIN:           [_____________] │
│                                 │
│  [Login]  [Register]            │
│  [Forgot PIN?] [Forgot Name?]   │
└─────────────────────────────────┘
```
**What you see:** Login form with two fields
- **Business Name:** Your registered business
- **PIN:** 4-6 digit security code
- **Links:** Registration, forgot PIN/name recovery

---

### Screen 2: Main Dashboard
```
┌────────────────────────────────────────────┐
│ 💼 Your Business Name    👤 Logged In      │
├────────────────────────────────────────────┤
│ [📊 Sales] [👥 Customers] [📦 Inventory]  │
│ [📝 Quotes] [📊 Reports] [🤖 AI] [⚙️ Set] │
├────────────────────────────────────────────┤
│                                            │
│ Welcome! Choose a tab to start working     │
│                                            │
└────────────────────────────────────────────┘
```
**What you see:** 7 main navigation tabs
- Organize your work by function
- Each tab has sub-features

---

### Screen 3: Sales & Analytics Tab
```
┌──────────────────────────────────┐
│ 📊 Sales & Analytics             │
├──────────────────────────────────┤
│ [💳 New Sale] [💰 Refunds]       │
│ [📄 Sales Report] [📈 View Sales]│
│                                  │
│ Recent Transactions:             │
│ ┌──────────────────────────────┐ │
│ │ Date | Amount | Items | Pay  │ │
│ ├──────────────────────────────┤ │
│ │ 22/10 | $45.50 | 3 | Card   │ │
│ │ 22/10 | $12.00 | 1 | Cash   │ │
│ └──────────────────────────────┘ │
└──────────────────────────────────┘
```
**What you see:** 
- Transaction buttons at top
- Transaction history table below
- Click items for details

---

### Screen 4: New Sale Form
```
┌─────────────────────────────────┐
│ 💳 Create New Sale              │
├─────────────────────────────────┤
│                                 │
│ Add Items:                      │
│ Product: [Coffee ▼]             │
│ Quantity: [1]  [Add]            │
│                                 │
│ Items Added:                    │
│ • Coffee x1 ..................$5 │
│                                 │
│ Customer (Optional):            │
│ [Select customer ▼]             │
│                                 │
│ Payment Method:                 │
│ ○ Cash ○ Card ○ Mobile ○ Other │
│                                 │
│ Total: $5.00                    │
│ [Complete Sale]                 │
└─────────────────────────────────┘
```
**What you see:**
- Item selector and quantity
- Running total
- Customer selection
- Payment options
- Completion button

---

### Screen 5: Receipt Options
```
┌─────────────────────────────────┐
│ 📄 Receipt Generated            │
├─────────────────────────────────┤
│                                 │
│ Choose download format:         │
│ [📥 PDF] [📥 CSV] [📥 Text]     │
│                                 │
│ Receipt Preview:                │
│ =======================         │
│ PORTABLE POS RECEIPT            │
│ =======================         │
│ Coffee              x1    $5.00 │
│ TOTAL:                   $5.00  │
│ Date: 22/10/25 14:30:45        │
│ =======================         │
└─────────────────────────────────┘
```
**What you see:**
- Download format options
- Receipt preview
- All transaction details

---

### Screen 6: Customers Tab
```
┌──────────────────────────────────┐
│ 👥 Customers                     │
├──────────────────────────────────┤
│ [➕ Add Customer] [📊 Report]    │
│                                  │
│ Customer List:                   │
│ ┌────────────────────────────┐   │
│ │ Name | Email | Phone      │   │
│ ├────────────────────────────┤   │
│ │ John | john@... | 555-1234│   │
│ │ Jane | jane@... | 555-5678│   │
│ └────────────────────────────┘   │
│                                  │
│ Click to view purchase history   │
└──────────────────────────────────┘
```
**What you see:**
- Customer management interface
- List of all customers
- Contact information
- Click to view details

---

### Screen 7: AI Analytics
```
┌──────────────────────────────────┐
│ 🤖 AI Analytics                  │
├──────────────────────────────────┤
│ [📈 Forecast] [👥 Customers]    │
│ [📦 Menu] [📢 Marketing] [⚠️ Anomaly]│
│                                  │
│ 📈 Sales Forecast:               │
│ ┌────────────────────────────┐   │
│ │ Based on your trends:      │   │
│ │ • Next week: +15% sales    │   │
│ │ • Peak day: Friday         │   │
│ │ • Stock up: Coffee (high)  │   │
│ │                            │   │
│ │ Recommendation: Create     │   │
│ │ weekend special on coffee! │   │
│ └────────────────────────────┘   │
└──────────────────────────────────┘
```
**What you see:**
- AI analysis tabs
- Generated insights
- Recommendations
- Data-driven suggestions

---

### Screen 8: Settings Tab
```
┌──────────────────────────────────┐
│ ⚙️ Settings                      │
├──────────────────────────────────┤
│ [General] [Theme] [Export] [Backup] │
│                                  │
│ General Settings:                │
│ Business Name: My Shop           │
│ Email: owner@myshop.com          │
│ Timezone: UTC-5                  │
│                                  │
│ [Save Changes]                   │
│                                  │
│ Theme:                           │
│ ○ Light Mode  ○ Dark Mode        │
└──────────────────────────────────┘
```
**What you see:**
- Configuration options
- Theme switcher
- Export/backup buttons
- Account settings

---

### Color Scheme & Icons

**Light Mode Colors:**
- Background: White
- Sidebar: Light gray
- Buttons: Blue
- Success: Green
- Warning: Orange
- Error: Red

**Dark Mode Colors:**
- Background: Dark gray
- Sidebar: Darker gray
- Buttons: Light blue
- Text: White/Light gray

**Common Icons:**
- 📊 Analytics/Dashboard
- 💳 Payments/Sales
- 👥 People/Customers
- 📦 Products/Inventory
- 🤖 AI/Intelligence
- ⚙️ Settings/Configuration
- 💰 Money/Refunds
- 📄 Documents/Reports

---

## Mobile Layout Notes

**On Phone (Landscape):**
- Tabs arranged vertically in sidebar
- Data tables become scrollable
- Buttons stack naturally

**On Phone (Portrait):**
- Full-width forms
- Vertical tab navigation
- Optimized touch targets

**Best Experience:**
- Use landscape for data entry
- Use portrait for viewing
- Zoom to 100% (not pinched)


|----------|--------|
| `Ctrl + S` | Save transaction |
| `Ctrl + P` | Print receipt |
| `Ctrl + R` | Refresh data |
| `Ctrl + E` | Export report |
| `Escape` | Close dialog/modal |

---

## FAQ

**Q: Is my data secure?**
A: Yes! All data is encrypted in MongoDB and protected with PIN authentication.

**Q: Can I access from outside my WiFi?**
A: Currently limited to local network. For remote access, you'd need to deploy on a server.

**Q: How much data can I store?**
A: MongoDB Atlas free tier allows up to 512MB. Upgrade plans available for more storage.

**Q: Can I have multiple users?**
A: Each business has its own PIN. Multiple people can use the same business account.

**Q: What payment methods are supported?**
A: Cash, Card, Mobile Money, and Other (custom).

**Q: Can I edit past transactions?**
A: Yes, most transaction details can be edited. Refunds are issued for reversals.

**Q: How do I backup my data?**
A: Use Settings → Backup or export reports regularly.

---

## Support

For issues or questions:
1. Check this manual
2. Review error messages in the app
3. Check browser console (F12) for technical errors
4. Review MongoDB Atlas dashboard for database issues
5. Check your internet connection

---

**Last Updated:** October 22, 2025
**App Version:** 1.0.0
**Status:** Production Ready ✅

