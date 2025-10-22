# Portable POS - Troubleshooting Flowchart

Use this guide to diagnose and fix common issues.

---

## Main Troubleshooting Flow

```
START: App Not Working?
    │
    ├─→ Is the app even running?
    │    ├─ YES → Go to "App Running Issues"
    │    └─ NO  → Go to "Startup Issues"
    │
    ├─→ Can you see the login page?
    │    ├─ YES → Go to "Login Issues"
    │    └─ NO  → Go to "Connection Issues"
    │
    └─→ Are you logged in but things aren't working?
         └─→ Go to "Feature Issues"
```

---

## 1. STARTUP ISSUES

### Problem: App Won't Start

```
App won't start?
    │
    ├─→ Do you see "No module named..."?
    │    │
    │    └─→ SOLUTION: Missing Python packages
    │         $ pip install -r requirements.txt
    │         $ streamlit run frontend/app.py
    │
    ├─→ Do you see "ModuleNotFoundError: No module named 'backend'"?
    │    │
    │    └─→ SOLUTION: Working directory wrong
    │         Make sure you're in project ROOT
    │         $ cd C:\Users\reine\Projects\Capstone
    │         $ streamlit run frontend/app.py
    │
    ├─→ Do you see "Address already in use"?
    │    │
    │    └─→ SOLUTION: Port 8502 is in use
    │         Option A: Kill other Streamlit process
    │         $ streamlit run frontend/app.py --server.port 8503
    │         Option B: Wait 30 seconds and try again
    │
    ├─→ Do you see "SSL: CERTIFICATE_VERIFY_FAILED"?
    │    │
    │    └─→ SOLUTION: SSL certificate issue
    │         This is normal on first run
    │         Browser should auto-fix
    │         If persists: Check frontend/.streamlit/config.toml
    │
    └─→ Virtual environment not activated?
         │
         └─→ SOLUTION: Activate venv first
              $ .\venv\Scripts\Activate.ps1
              $ streamlit run frontend/app.py
```

---

## 2. CONNECTION ISSUES

### Problem: Can't Access the App

```
Can't see login page?
    │
    ├─→ Is the app running in terminal?
    │    ├─ YES → Continue below
    │    └─ NO  → Go to "Startup Issues"
    │
    ├─→ Are you using correct URL?
    │    │
    │    ├─ Local:  https://localhost:8502 ✓
    │    ├─ Local:  http://127.0.0.1:8502 ✓
    │    ├─ Mobile: https://192.168.1.4:8502 (check IP!)
    │    └─ Wrong:  http://192.168.1.4:8502 (should be https)
    │
    ├─→ Browser shows SSL warning?
    │    │
    │    └─→ SOLUTION: Expected for self-signed cert
    │         Click "Advanced" → "Proceed anyway"
    │         Or ignore warning
    │
    ├─→ Still can't connect?
    │    │
    │    └─→ SOLUTION: Check firewall
    │         Windows: Settings → Firewall → Allow app
    │         Or temporarily disable firewall to test
    │
    ├─→ On mobile but can't reach?
    │    │
    │    └─→ SOLUTION: Network issues
    │         1. Phone on same WiFi? (required!)
    │         2. Correct IP? (ping computer from phone)
    │         3. Router blocking local traffic?
    │         4. Try restarting router
    │
    └─→ Connection times out?
         │
         └─→ SOLUTION: App crashed or hung
              Restart: Ctrl+C in terminal
              $ streamlit run frontend/app.py
```

---

## 3. LOGIN ISSUES

### Problem: Can't Login

```
Login not working?
    │
    ├─→ Error: "Business not found"?
    │    │
    │    └─→ SOLUTION: Business name wrong
    │         Check spelling (case-sensitive)
    │         Or register new business
    │
    ├─→ Error: "Invalid PIN"?
    │    │
    │    └─→ SOLUTION: PIN incorrect
    │         PIN is case-sensitive
    │         Count digits carefully
    │         Click "Forgot PIN?" to reset
    │
    ├─→ Error: "MongoDB connection failed"?
    │    │
    │    └─→ SOLUTION: Database unreachable
    │         1. Check .env file exists
    │         2. Check MONGODB_URI is correct
    │         3. Verify MongoDB Atlas cluster running
    │         4. Check internet connection
    │         5. Verify IP whitelisted in MongoDB
    │
    ├─→ Forgot PIN?
    │    │
    │    └─→ SOLUTION: Use password reset
    │         Click "Forgot PIN?" button
    │         Enter business name
    │         Create new PIN
    │         Login with new PIN
    │
    ├─→ Forgot business name?
    │    │
    │    └─→ SOLUTION: Recover business name
    │         Click "Forgot Business Name?"
    │         Enter email used at signup
    │         System will show businesses
    │
    └─→ Still can't register?
         │
         └─→ SOLUTION: Database issues
              Verify MongoDB connection
              Check .env MONGODB_URI format:
              mongodb+srv://user:pass@cluster.mongodb.net/db_name
```

---

## 4. DATABASE ISSUES

### Problem: Database Connection Problems

```
MongoDB errors?
    │
    ├─→ "Failed to connect to MongoDB"?
    │    │
    │    ├─ SOLUTION: Check MongoDB URI format
    │    │  Format: mongodb+srv://USER:PASS@cluster.mongodb.net/db
    │    │  Replace: USER, PASS, cluster name
    │    │
    │    ├─ SOLUTION: IP whitelist
    │    │  MongoDB Atlas → Network Access
    │    │  Add your IP: 0.0.0.0/0 (or specific IP)
    │    │
    │    ├─ SOLUTION: Cluster running?
    │    │  MongoDB Atlas → Clusters
    │    │  Check cluster is "Available" (not paused)
    │    │
    │    └─ SOLUTION: Password special chars?
    │       If password has @#$%, URL-encode them:
    │       @ = %40, # = %23, $ = %24, % = %25
    │
    ├─→ "Transactions not saving"?
    │    │
    │    └─→ SOLUTION: Connection drops mid-transaction
    │         Check internet stability
    │         Try transaction again
    │         Restart app if repeated
    │
    ├─→ "Slow database queries"?
    │    │
    │    └─→ SOLUTION: Too much data or slow connection
    │         Try reducing date range
    │         Upgrade MongoDB plan if many records
    │         Check internet speed
    │
    └─→ "Duplicate key error"?
         │
         └─→ SOLUTION: Data conflict
              Contact support or manually delete duplicate
              Restart app to refresh
```

---

## 5. FEATURE ISSUES

### Problem: Features Not Working

```
Feature broken?
    │
    ├─→ "AI Features not working"?
    │    │
    │    ├─ SOLUTION: Check Google API key
    │    │  .env file has GOOGLE_API_KEY?
    │    │  Key is correct? (no typos)
    │    │
    │    ├─ SOLUTION: API quota exceeded
    │    │  Google Cloud → Quotas
    │    │  Check if quota exceeded
    │    │  Upgrade if needed
    │    │
    │    └─ SOLUTION: API not enabled
    │       Google Cloud → APIs & Services
    │       Enable "Google Generative AI API"
    │
    ├─→ "Can't create new sale"?
    │    │
    │    ├─ SOLUTION: No products in menu
    │    │  Add items first in Inventory tab
    │    │
    │    ├─ SOLUTION: MongoDB error
    │    │  Check database connection
    │    │  Restart app
    │    │
    │    └─ SOLUTION: Form validation
    │       Fill all required fields
    │       Select at least one product
    │       Choose payment method
    │
    ├─→ "Can't export to Excel"?
    │    │
    │    ├─ SOLUTION: openpyxl not installed
    │    │  $ pip install openpyxl
    │    │
    │    ├─ SOLUTION: Insufficient disk space
    │    │  Free up disk space
    │    │
    │    └─ SOLUTION: Try PDF instead
    │       PDF doesn't need openpyxl
    │
    ├─→ "Charts/graphs not showing"?
    │    │
    │    ├─ SOLUTION: Refresh page
    │    │  Press F5 or click refresh
    │    │
    │    ├─ SOLUTION: No data yet
    │    │  Create some transactions first
    │    │
    │    └─ SOLUTION: Date range too narrow
    │       Expand date range in filters
    │
    ├─→ "Can't see transactions"?
    │    │
    │    ├─ SOLUTION: Wrong date range
    │    │  Check date filter
    │    │  Expand to see older transactions
    │    │
    │    ├─ SOLUTION: Wrong business logged in
    │    │  Logout and login again
    │    │
    │    └─ SOLUTION: Database sync issue
    │       Refresh page
    │       Restart app
    │
    └─→ "Settings not saving"?
         │
         ├─ SOLUTION: Database connection
         │  Check MongoDB connection
         │
         └─ SOLUTION: Browser storage
            Clear browser cache
            Hard refresh (Ctrl+Shift+R)
```

---

## 6. MOBILE-SPECIFIC ISSUES

### Problem: Can't Access on Mobile

```
Mobile not working?
    │
    ├─→ "Can't reach https://192.168.1.4:8502"?
    │    │
    │    ├─ SOLUTION: Not on same WiFi
    │    │  Phone must be on SAME WiFi as computer
    │    │  Check WiFi name in phone settings
    │    │
    │    ├─ SOLUTION: Wrong IP address
    │    │  Find correct IP:
    │    │  • Terminal: $ ipconfig
    │    │  • Look for: IPv4 Address (192.168.x.x)
    │    │
    │    ├─ SOLUTION: Port blocked
    │    │  Try: https://192.168.1.4:8502/
    │    │  Or from terminal, get actual URL from streamlit output
    │    │
    │    └─ SOLUTION: Firewall blocking
    │       Disable firewall temporarily to test
    │
    ├─→ "SSL Certificate Error on Phone"?
    │    │
    │    └─→ SOLUTION: Expected with self-signed cert
    │         Android: Tap "Advanced" → "Proceed to IP"
    │         iOS: Tap "Details" → "Visit this website"
    │         (Safe because it's local network only)
    │
    ├─→ "App very slow on mobile"?
    │    │
    │    ├─ SOLUTION: WiFi signal weak
    │    │  Move closer to router
    │    │
    │    ├─ SOLUTION: Too many users
    │    │  Disconnect other devices
    │    │
    │    └─ SOLUTION: Browser cache
    │       Clear phone browser cache
    │       Hard refresh (pull down to refresh)
    │
    ├─→ "Can't scroll/interact on mobile"?
    │    │
    │    ├─ SOLUTION: Zoom level wrong
    │    │  Pinch zoom to 100%
    │    │
    │    ├─ SOLUTION: Browser zoom
    │    │  Settings → Zoom → 100%
    │    │
    │    └─ SOLUTION: Try different browser
    │       Chrome, Safari, Firefox
    │
    └─→ "Mobile keeps disconnecting"?
         │
         ├─ SOLUTION: WiFi keeps dropping
         │  Check router/WiFi stability
         │
         └─ SOLUTION: Session timeout
            App times out after 30 min inactivity
            Login again
```

---

## 7. PERFORMANCE ISSUES

### Problem: App Is Slow

```
Performance problem?
    │
    ├─→ "Page loads slowly"?
    │    │
    │    ├─ SOLUTION: Too much data
    │    │  Use date filters to reduce data
    │    │  Example: Show last 7 days only
    │    │
    │    ├─ SOLUTION: Internet slow
    │    │  Test speed: speedtest.net
    │    │  Should be >10 Mbps for smooth experience
    │    │
    │    ├─ SOLUTION: Many transactions
    │    │  If 1000s of records: Upgrade MongoDB
    │    │  Or archive old data
    │    │
    │    └─ SOLUTION: Browser cache
    │       Clear cache: Ctrl+Shift+Delete
    │       Hard refresh: Ctrl+Shift+R
    │
    ├─→ "Database queries timeout"?
    │    │
    │    ├─ SOLUTION: Reduce data range
    │    │  Query fewer records
    │    │  Narrow date range
    │    │
    │    └─ SOLUTION: MongoDB too slow
    │       Check indexes in MongoDB
    │       Consider upgrading tier
    │
    ├─→ "Charts rendering slow"?
    │    │
    │    ├─ SOLUTION: Reduce data points
    │    │  Fewer transactions = faster charts
    │    │
    │    └─ SOLUTION: Browser performance
    │       Use Chrome or Edge
    │       Close other tabs
    │
    └─→ "Mobile experience very laggy"?
         │
         ├─ SOLUTION: Reduce viewport
         │  Use portrait mode (narrower)
         │
         ├─ SOLUTION: Disable background apps
         │  Close other apps on phone
         │
         └─ SOLUTION: Restart everything
            Restart phone
            Restart app
            Reconnect WiFi
```

---

## Emergency Fixes (When All Else Fails)

### Nuclear Options

```
Last resort:

1. RESTART EVERYTHING
   $ Ctrl+C (stop app)
   $ Close browser completely
   $ Restart computer (optional)
   $ .\venv\Scripts\Activate.ps1
   $ streamlit run frontend/app.py

2. CLEAR CACHE & COOKIES
   Browser: Ctrl+Shift+Delete → Clear all time
   Streamlit: Delete ~/.streamlit/config.toml cache

3. REINSTALL DEPENDENCIES
   $ pip uninstall -r requirements.txt -y
   $ pip install -r requirements.txt
   $ streamlit run frontend/app.py

4. CHECK LOGS
   Look at terminal output for error messages
   Google the error message
   Check MongoDB Atlas logs

5. DATABASE RESET (LAST RESORT)
   Delete collection in MongoDB
   Start fresh with no data
   WARNING: Deletes all records!

6. FRESH CLONE
   If all else fails:
   $ git clone https://github.com/reinedujura/Portable-POS.git Portable-POS-Fresh
   $ cd Portable-POS-Fresh
   $ python -m venv venv
   $ .\venv\Scripts\Activate.ps1
   $ pip install -r requirements.txt
   $ Copy .env to new folder
   $ streamlit run frontend/app.py
```

---

## When to Seek Help

If you've tried all above steps:

1. **Check GitHub Issues:** https://github.com/reinedujura/Portable-POS/issues
2. **Review Error Logs:** Terminal output often has solution
3. **Test Basic Connectivity:**
   ```
   $ ping 8.8.8.8          (Internet OK?)
   $ ping mongodb.com      (MongoDB accessible?)
   ```
4. **Verify Credentials:**
   - MongoDB URI correct?
   - Gemini API key valid?
   - Business name exact match?

---

## Quick Reference: Common Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Run the app
streamlit run frontend/app.py

# Check Python version
python --version

# Deactivate virtual environment
deactivate

# Check if port is in use
netstat -ano | findstr :8502

# Kill process on port 8502
taskkill /PID <PID> /F

# Check MongoDB connection
python -c "from pymongo import MongoClient; MongoClient('YOUR_URI')"

# Clear Streamlit cache
rm -r ~/.streamlit

# Hard refresh browser
Ctrl + Shift + R

# Check local IP
ipconfig
```

---

**Last Updated:** October 22, 2025
**For Version:** 1.0.0

