import requests
import time
import logging
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────

DISCORD_WEBHOOKS = [
    "https://discord.com/api/webhooks/1492672980667469866/Ms1TAesX5lkShgUFyN-OF2coBFgwSP3Y6gZSbSE0O5jpBnKzvYE4k1pIaNnwULxzDbLp",
    "https://discordapp.com/api/webhooks/1493069417783885824/VpNsPGKC25BJysQsWPwmqY5uiBDr1GSz-pEBNX5JHxUuUZZdA8ryVaX6Gp-tJk2vtpyK"
]

PUSHOVER_USER_KEY  = "u8mo5ey3zc4q2spwkv9xkthvfqocgo"
PUSHOVER_API_TOKEN = "avgj8s6byu5ruwt1p5vnbjhpnuarzq"

ROBLOX_COOKIE = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhADIhwKBGR1aWQSFDE2NzM3NDA1MzY4MjA5NDM5MDY1KAQ.ZHurh_lmzfRsh2GCPONwzfxitF9u5PQZmWdOaEge9gtDyFwoCeOdHY7HSAdwslIaclPzSZ5UjSlITpY1OvTdxzcj0J726WBjYi0XIkK3VbYjeuvi5JkwB7YmrTvvAyRXud55VE7Jt7HIbQ-0A6mTlls9QaCVVbT4cJ3okOZwsZXGK9i_mJnWncZXIDZfp9c5Gjbri-fU5PCq0kTBa4ZDU2purhlWGIW210agIT5UB7kBg92JiKn3eVnCHxmRkVeSEwg5HvDE3zxECtLCGmwoOt3cVV4zmX4srhh9dsjj62xXGkPMz97zH_R205eO_ybrCNYO53ukEnAgKSWFc43kQtUOUwTJZsyhUzoWtjWq4C7S8VFfKck6Y9kg7dMAQYycnX7Mp4GSntby_LEzkvPYeiHL7luHSOQj4iAU53nBgM9SpyiBOAn_rx8omBj335saUcfZmTcWmD21o8rhdUdibqMLiI3-xLfX1a04cnnuZ9JnLiQD4aPQfKnS1Tz2Jzv2DjZGAsy0bdXIo-imXvEMCWx6S74m2iFM8v2ZTga_k1jZkNj5S1w6i6UCIHuWJWy3xv5QDgg32CcGmjsmIiyZ54tu0DODsdepu3f3gv_c-DUKImJEjUjO-QBmFLzqyUBV5J43atxaccNmrKchL4ftlDg8SLwEq2_miXZ4DbRrByzV_urFeFT4PM66YUks4gZ9C1MdOjPhsCY1tRZgdto4clUmJZxJcdb0PUDKGllIDq1Hy0LKbVjrmjXuOD8GDTA_5-5H7WbQsSCnyGGMKS64DVVLrWNNDSWD-t--1Ss9_P_MeOdxRStSXvKxeJQre4jpOb04Qg"

ROBLOX_USER_ID = 338528360
TARGET_PLACE_ID = 1458767429
FETCH_INTERVAL = 20

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

def send_discord(title: str, message: str, ping_everyone: bool = False) -> None:
    prefix = "@everyone " if ping_everyone else ""
    for webhook in DISCORD_WEBHOOKS:
        try:
            response = requests.post(
                webhook,
                json={"content": f"{prefix}**{title}**\n{message}"},
                timeout=10
            )
            if response.status_code == 204:
                logging.info(f"Discord notification sent to {webhook[:50]}...")
            else:
                logging.error(f"Discord error {response.status_code}: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Failed to send to webhook: {e}")

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
#  SEND ALL
# ─────────────────────────────────────────

def send_notification(title: str, message: str, ping_everyone: bool = False, priority: int = 0):
    send_discord(title, message, ping_everyone)
    send_pushover(title, message, priority)

# ─────────────────────────────────────────
#  ROBLOX API FETCH
# ─────────────────────────────────────────

def fetch_api_data() -> dict | None:
    try:
        response = requests.post(
            "https://presence.roblox.com/v1/presence/users",
            json={"userIds": [ROBLOX_USER_ID]},
            headers={
                "Cookie": f".ROBLOSECURITY={ROBLOX_COOKIE}"
            },
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

def format_message(data: dict) -> tuple[str, str, bool]:
    try:
        user = data["userPresences"][0]
        presence_type = user.get("userPresenceType", 0)
        last_location = user.get("lastLocation", "Unknown")
        place_id = user.get("rootPlaceId")
        timestamp = datetime.now().strftime("%H:%M:%S")

        status_map = {
            0: "Offline 🔴",
            1: "Online 🟡",
            2: "In Game 🟢",
            3: "In Studio 🔵"
        }
        status = status_map.get(presence_type, "Unknown")

        in_target_game = presence_type == 2 and place_id == TARGET_PLACE_ID
        ping_everyone = in_target_game

        if in_target_game:
            title = f"🎮 Now Playing Target Game! — {timestamp}"
        else:
            title = f"Roblox Alert — {timestamp}"

        message = f"Status: {status}\nLocation: {last_location}"
        return title, message, ping_everyone

    except Exception as e:
        return "Roblox Alert", f"Could not parse response: {e}", False

# ─────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────

def main():
    logging.info("Starting Roblox presence monitor...")
    logging.info(f"Monitoring user ID: {ROBLOX_USER_ID}")
    logging.info(f"Pinging @everyone only when in place ID: {TARGET_PLACE_ID}")
    logging.info(f"Checking every {FETCH_INTERVAL} seconds")

    last_status = None

    while True:
        data = fetch_api_data()

        if data:
            user = data["userPresences"][0]
            current_status = user.get("userPresenceType", 0)
            current_place = user.get("rootPlaceId")
            current_state = (current_status, current_place)

            if current_state != last_status:
                title, message, ping_everyone = format_message(data)
                send_notification(title, message, ping_everyone=ping_everyone)
                last_status = current_state
            else:
                logging.info(f"Status unchanged ({current_status}), no notification sent.")
        else:
            send_notification(
                "⚠️ Roblox API Failed",
                f"Could not reach Roblox presence API at {datetime.now().strftime('%H:%M:%S')}",
                ping_everyone=False,
                priority=1
            )

        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
