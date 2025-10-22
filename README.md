# Portable POS

A professional Streamlit-based Point-of-Sale system with FastAPI REST API backend and MongoDB integration.

## Features

- ✅ Real-time sales tracking and analytics
- ✅ Customer management system
- ✅ AI-powered insights (Google Gemini integration)
- ✅ REST API with 17 endpoints
- ✅ Comprehensive test coverage (70%+)
- ✅ SSL/TLS security
- ✅ Production-ready logging

## Tech Stack

- **Frontend:** Streamlit (Python)
- **Backend:** FastAPI (REST API)
- **Database:** MongoDB Atlas
- **AI/LLM:** Google Gemini 1.5 Flash
- **Testing:** pytest with 70%+ coverage
- **Python:** 3.x with type hints

## Project Structure

```
Portable-POS/
├── frontend/
│   ├── app.py              # Streamlit UI (9,700+ lines)
│   ├── .streamlit/         # Configuration
│   └── __init__.py
├── backend/
│   ├── api.py              # FastAPI REST API (17 endpoints)
│   ├── services/           # Business logic (3 services)
│   ├── database/           # MongoDB integration
│   ├── models/             # Data models (Pydantic)
│   ├── agents/             # AI agents
│   ├── utils/              # Utility functions
│   ├── config/             # Logging configuration
│   └── constants.py        # App constants
├── tests/
│   ├── unit/               # Unit tests (20+ cases)
│   └── integration/        # Integration tests (9+ cases)
├── static/                 # CSS, JS, images
├── backup/                 # Version backups
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Installation

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/reinedujura/Portable-POS.git
   cd Portable-POS
   ```

2. **Create and activate virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your MongoDB URI and API keys
   ```

## Usage

### Run Streamlit App

From the project root directory:
```powershell
streamlit run frontend/app.py --server.address=0.0.0.0
```

Configuration is in `frontend/.streamlit/config.toml`

### Access the Application

- **On your computer:**
  - 🌐 `https://localhost:8502` (Recommended)
  - 🌐 `https://127.0.0.1:8502`

- **On your phone (same WiFi):**
  - 📱 `https://192.168.1.4:8502` (your local IP)

### Run Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=backend
```

### FastAPI REST API

The FastAPI server can be run separately:
```powershell
python -m uvicorn backend.api:app --reload
```

Then access: `http://localhost:8000/docs` (Swagger UI)

## Architecture

- **Layered Architecture:** API → Services → Database
- **Service-Oriented:** Separate services for transactions, customers, users
- **Type-Safe:** Full type hints throughout codebase
- **Tested:** 70%+ code coverage with pytest
- **Logged:** Production logging with file rotation

## Configuration

### Environment Variables (.env)

```env
MONGODB_URI=your_mongodb_connection_string
GOOGLE_API_KEY=your_gemini_api_key
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Streamlit Config (frontend/.streamlit/config.toml)

- Server address: `0.0.0.0`
- Port: `8502`
- SSL certificates: `../certs/` (mkcert)

## License

MIT License - See LICENSE file for details

## Author

reinedujura

---

**Last Updated:** October 22, 2025
