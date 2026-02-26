from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


def send_telegram_message(bot_token: str, chat_id: str, text: str, timeout: int = 12) -> tuple[bool, str]:
    token = (bot_token or "").strip()
    cid = (chat_id or "").strip()
    msg = (text or "").strip()

    if not token:
        return False, "Missing bot token"
    if not cid:
        return False, "Missing chat id"
    if not msg:
        return False, "Message is empty"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": cid,
            "text": msg,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    request = urllib.request.Request(url=url, data=payload, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
        data = json.loads(body)
        if data.get("ok"):
            return True, "Sent"
        return False, str(data.get("description", "Telegram API error"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return False, f"HTTP {exc.code}: {detail}"
    except Exception as exc:
        return False, str(exc)
