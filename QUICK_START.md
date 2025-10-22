# Portable POS - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites
- Python 3.7+ installed
- MongoDB Atlas account (free tier: https://www.mongodb.com/cloud/atlas)
- Google Gemini API key (free: https://ai.google.dev/)
- Internet connection

## Step-by-Step Setup

### Step 1: Clone & Setup (2 minutes)

```powershell
# Clone the repository
git clone https://github.com/reinedujura/Portable-POS.git
cd Portable-POS

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies (1 minute)

```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment (1 minute)

Create a `.env` file in the project root:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/portable_pos_db
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Getting MongoDB URI:**
1. Go to https://cloud.mongodb.com
2. Create free cluster
3. Click "Connect"
4. Copy connection string
5. Replace `<password>` with your password

**Getting Gemini API Key:**
1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create new project
4. Copy API key to `.env`

### Step 4: Run the App (1 minute)

```powershell
streamlit run frontend/app.py --server.address=0.0.0.0
```

**You'll see:**
```
Local URL: http://localhost:8502
Network URL: http://192.168.1.7:8502
```

### Step 5: Access & Register (30 seconds)

- Open browser: `https://localhost:8502`
- Click **Register**
- Enter business name (e.g., "My Shop")
- Create 4-6 digit PIN
- Click **Register**

✅ **Done!** You're ready to use Portable POS!

---

## First 3 Actions to Try

### 1️⃣ Add a Product
- Go to **Inventory** → **Menu Management**
- Click **➕ Create** (under any category)
- Add product: "Coffee" | Price: $5 | Quantity: 10
- Click **Save**

### 2️⃣ Create a Sale
- Go to **Sales & Analytics** → **💳 New Sale**
- Add the Coffee product (quantity: 1)
- Click **Complete Sale**
- Download receipt (PDF)

### 3️⃣ View Analytics
- Go to **Sales & Analytics** → **📊 Metrics**
- See your first sale in the dashboard!

---

## Mobile Access

Access the app on your phone:

1. Ensure phone is on **same WiFi** as computer
2. Open browser on phone
3. Go to: `https://192.168.1.4:8502` (replace with your IP)
4. Accept SSL warning (self-signed certificate)
5. Login with your PIN

---

## Common First-Time Issues

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` again |
| "MongoDB connection failed" | Check `.env` file has correct URI |
| "API key error" | Verify Gemini API key is correct |
| "Port 8502 already in use" | Change port or kill other Streamlit processes |
| "Can't access on mobile" | Check IP address, ensure same WiFi |

---

## Next Steps

1. ✅ Add more products to your menu
2. ✅ Practice creating sales
3. ✅ Add customers for tracking
4. ✅ Explore AI Analytics
5. ✅ Generate your first report

---

**Need more help?** See the full `USER_MANUAL.md` for detailed documentation.

