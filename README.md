# Portable POS

Follow the steps below to ensure the project is set up correctly:

## Steps to Set Up the Project

1. **Activate the Virtual Environment**:
   - Run the following commands:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

2. **Update Project-Specific Files**:
   - Edit `README.md` to reflect the project details.
   - Update `.env` with project-specific environment variables.

3. **Run the Application**:
   - **powershell**
   streamlit run frontend/app.py --server.address=0.0.0.0

   (Configuration is in `frontend/.streamlit/config.toml`)
     ```

4. **Access the Application**:
   - **On your computer:**
     - ✅ `https://localhost:8502` (Recommended)
     - ✅ `https://127.0.0.1:8502`
   
   - **On your phone (same WiFi):**
     - 📱 `https://192.168.1.4:8502` (your local IP)

## Folder Structure

- `main.py`: Entry point for the application.
- `mongodb.py`: MongoDB integration.
- `streamlit.py`: Streamlit UI.
- `venv/`: Virtual environment folder.
- `.env`: Environment variables file.
- `requirements.txt`: Python dependencies.

## Theme Visual Tests

There is a Playwright-based visual test to capture screenshots while cycling the app themes.

Setup:

1. Install Playwright and browsers:

   ```powershell
   pip install playwright
   playwright install
   ```

2. Ensure the Streamlit app is running locally (default http://localhost:8505). If using a different port, set APP_URL environment variable.

Run the test:

```powershell
# from project root
python tests/theme_visual_test.py
``` 

Screenshots will be saved to `tests/screenshots`.
