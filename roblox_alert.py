import requests
import time
import logging
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1492672980667469866/Ms1TAesX5lkShgUFyN-OF2coBFgwSP3Y6gZSbSE0O5jpBnKzvYE4k1pIaNnwULxzDbLp"

PUSHOVER_USER_KEY  = "u8mo5ey3zc4q2spwkv9xkthvfqocgo"
PUSHOVER_API_TOKEN = "avgj8s6byu5ruwt1p5vnbjhpnuarzq"

ROBLOX_USER_ID = 338528360

FETCH_INTERVAL = 10

# ─────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# ─────────────────────────────────────────
#  DISCORD NOTIFICATION
# ─────────────────────────────────────────

def send_discord(title: str, message: str) -> bool:
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": f"**{title}**\n{message}"},
            timeout=10
        )
        if response.status_code == 204:
            logging.info("Discord notification sent successfully.")
            return True
        else:
            logging.error(f"Discord error {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Failed to send Discord notification: {e}")
        return False

# ─────────────────────────────────────────
#  PUSHOVER NOTIFICATION
# ─────────────────────────────────────────

def send_pushover(title: str, message: str, priority: int = 0) -> bool:
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token":    PUSHOVER_API_TOKEN,
                "user":     PUSHOVER_USER_KEY,
                "title":    title,
                "message":  message,
                "priority": priority,
            },
            timeout=10
        )
        if response.status_code == 200:
            logging.info("Pushover notification sent successfully.")
            return True
        else:
            logging.error(f"Pushover error {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Failed to send Pushover notification: {e}")
        return False

# ─────────────────────────────────────────
#  SEND BOTH
# ─────────────────────────────────────────

def send_notification(title: str, message: str, priority: int = 0):
    send_discord(title, message)
    send_pushover(title, message, priority)

# ─────────────────────────────────────────
#  ROBLOX API FETCH
# ─────────────────────────────────────────

def fetch_api_data() -> dict | None:
    try:
        response = requests.post(
            "https://presence.roblox.com/v1/presence/users",
            json={"userIds": [ROBLOX_USER_ID]},
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"API fetch successful — status {response.status_code}")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API fetch failed: {e}")
        return None

# ─────────────────────────────────────────
#  FORMAT ALERT MESSAGE
# ─────────────────────────────────────────

def format_message(data: dict) -> tuple[str, str]:
    try:
        user = data["userPresences"][0]
        presence_type = user.get("userPresenceType", 0)
        last_location = user.get("lastLocation", "Unknown")
        timestamp = datetime.now().strftime("%H:%M:%S")

        status_map = {
            0: "Offline 🔴",
            1: "Online 🟡",
            2: "In Game 🟢",
            3: "In Studio 🔵"
        }
        status = status_map.get(presence_type, "Unknown")

        title   = f"Roblox Alert — {timestamp}"
        message = f"Status: {status}\nLocation: {last_location}"
        return title, message

    except Exception as e:
        return "Roblox Alert", f"Could not parse response: {e}"

# ─────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────

def main():
    logging.info("Starting Roblox presence monitor...")
    logging.info(f"Monitoring user ID: {ROBLOX_USER_ID}")
    logging.info(f"Checking every {FETCH_INTERVAL} seconds")

    last_status = None

    while True:
        data = fetch_api_data()

        if data:
            user = data["userPresences"][0]
            current_status = user.get("userPresenceType", 0)

            if current_status != last_status:
                title, message = format_message(data)
                send_notification(title, message)
                last_status = current_status
            else:
                logging.info(f"Status unchanged ({current_status}), no notification sent.")
        else:
            send_notification(
                "⚠️ Roblox API Failed",
                f"Could not reach Roblox presence API at {datetime.now().strftime('%H:%M:%S')}",
                priority=1
            )

        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
