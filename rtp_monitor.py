import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
import telegram
from datetime import datetime
import re

# Legge le variabili d'ambiente di Railway
BOT_TOKEN = os.getenv("7969789752:AAFxPcu7Ni1r0dRKA796-9F_BMLv9P59fbA")
CHAT_ID = os.getenv("-4925344956")
bot = telegram.Bot(token=BOT_TOKEN)

def get_rtp():
    url = 'https://www.casino.org/casinoscores/it/crazy-time/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        texts = soup.get_text()
        rtp_match = re.search(r'(\d+(?:,\d+)?)%', texts)
        if rtp_match:
            rtp_value = float(rtp_match.group(1).replace(',', '.'))
            return rtp_value
        return None
    except Exception as e:
        print("Errore get_rtp:", e)
        return None

def check_alert():
    rtp = get_rtp()
    if rtp and rtp < 68:
        message = f"🚨 RTP CRAZY TIME SOTTO 68%! {rtp}% - {datetime.now().strftime('%H:%M')}"
        bot.send_message(chat_id=CHAT_ID, text=message)
        print(message)
    else:
        print("RTP ok o non trovato:", rtp)

schedule.every(5).minutes.do(check_alert)
print("Monitoraggio avviato...")

while True:
    schedule.run_pending()
    time.sleep(1)
