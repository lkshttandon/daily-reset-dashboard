# Daily Reset Dashboard

Phone-friendly Streamlit dashboard for daily protocol tracking, insights, coaching, and Telegram reminders.

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
- `Reminders` tab for Telegram notifications (iPhone + Android via Telegram app)

## Project Structure
- `app.py` - Streamlit UI and app flow
- `reset_protocol.py` - Single editable `PROTOCOL` dictionary
- `db.py` - SQLite schema + data access helpers
- `coach_local.py` - local rule-based coach logic
- `telegram_notifier.py` - Telegram send helper (no external SDK required)
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
python -m py_compile app.py db.py coach_local.py reset_protocol.py telegram_notifier.py
```

## Telegram Mobile Notifications
1. In Telegram, create a bot with `@BotFather` and copy the bot token.
2. Get your personal chat id by messaging `@userinfobot` (or any chat-id bot).
3. In the app, open `Reminders` tab and set:
   - Enable Telegram reminders
   - Bot token
   - Chat ID
   - Daily reminder time (`HH:MM`, 24-hour format)
4. Save settings and use **Send Test Telegram Message**.

Note: Streamlit apps do not run background jobs continuously. Scheduled reminder sends happen when the app is opened/running after the configured time.

## Deploy to Streamlit Community Cloud
1. Push this repo to GitHub.
2. In Streamlit Community Cloud, click **New app**.
3. Select the repo/branch and set main file path to `app.py`.
4. Deploy.

## Security Note
- Do not commit secrets in source code.
