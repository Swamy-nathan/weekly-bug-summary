import os
import requests
import datetime
from dotenv import load_dotenv

# === Load environment variables (only needed locally) ===
load_dotenv()

# === CONFIGURATION ===
TRELLO_KEY = os.getenv('TRELLO_KEY').strip()
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN').strip()
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL').strip()
BOARD_ID = 'xjZb8QlW'

# Lists to track
TRACKED_LISTS = [
    "Frontend / UX", "Backend", "High Priority",
    "Regression", "Bug Fixed", "QA verified", "Production Released"
]

def fetch_cards():
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN, 'fields': 'id,name,idList'}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_lists():
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
    params = {'key': TRELLO_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return {lst['id']: lst['name'] for lst in response.json()}

def summarize_cards(cards, list_map):
    summary = {name: 0 for name in TRACKED_LISTS}
    for card in cards:
        list_name = list_map.get(card['idList'], 'Unknown')
        if list_name in summary:
            summary[list_name] += 1
    return summary

def send_to_slack(summary):
    today = datetime.datetime.now().strftime("%A, %d %B %Y")

    message = f"""✅ *Weekly QA Bug Tracker Summary* – _{today}_  
📊 *List-wise Card Count:*  

🖥️ *Frontend / UX - <@U0814V60X7Y>* — {summary['Frontend / UX']}  
🧠 *Backend - <@U07TR2T2XDW>* — {summary['Backend']}  

🚨 *High Priority* — {summary['High Priority']}  
🧪 *Regression* — {summary['Regression']}  

🛠️ *Bug Fixed* — {summary['Bug Fixed']}  
✅ *QA verified* — {summary['QA verified']}  
🚀 *Production Released* — {summary['Production Released']}  

🔗 *SCP Bug Tracker Trello Board:* https://trello.com/b/{BOARD_ID}
"""

    response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    
    if response.status_code == 200:
        print("✅ Slack message sent successfully.")
    else:
        print(f"❌ Failed to send Slack message. Status code: {response.status_code}")
        print("Response:", response.text)

def run_summary():
    print("📥 Fetching Trello data...")
    cards = fetch_cards()
    lists = fetch_lists()
    print("📊 Summarizing cards...")
    summary = summarize_cards(cards, lists)
    print("📤 Sending message to Slack...")
    send_to_slack(summary)

# Run only on Friday (weekday = 4)
if datetime.datetime.now().weekday() == 4:
    run_summary()
else:
    print("⏳ Not Friday. Script will run only on Fridays.")
