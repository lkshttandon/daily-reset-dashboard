# Daily Reset Dashboard

Phone-friendly Streamlit dashboard for daily protocol tracking, insights, and AI coaching.

## Features
- `Today` tab with grouped checklist sections:
  - Morning Routine
  - Morning Skincare
  - Daytime Habits
  - Evening Routine
  - Night Skincare
  - Bedtime
  - Weekly Checkpoint
- Auto-saving checkbox state and daily metrics to SQLite (`reset.db`)
- Daily progress bar (`done/total` and completion %)
- Reset button to clear today
- `Insights` tab:
  - Last 60 days completion % line chart
  - Last 14 days table (`done`, `total`, `%`)
  - Streak metric (consecutive days with completion >= 70%)
- `Coach` tab using local rule-based logic for two goal modes:
  - Fat loss + stable energy
  - Muscle gain + performance

## Project Structure
- `app.py` - Streamlit UI and app flow
- `reset_protocol.py` - Single editable `PROTOCOL` dictionary
- `db.py` - SQLite schema + data access helpers
- `coach_local.py` - local rule-based coach logic
- `.streamlit/config.toml` - dark theme + minimal toolbar
- `requirements.txt` - dependencies for local and cloud deploy

## Local Run
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run app:
   ```bash
   streamlit run app.py
   ```

## Quick Self-Check
Run a syntax check:
```bash
python -m py_compile app.py db.py coach.py reset_protocol.py
```

## Deploy to Streamlit Community Cloud
1. Push this repo to GitHub.
2. In Streamlit Community Cloud, click **New app**.
3. Select the repo/branch and set main file path to `app.py`.
4. Deploy.

## Security Note
- Do not commit secrets in source code.
