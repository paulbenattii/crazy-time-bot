import requests
from bs4 import BeautifulSoup
import schedule
import time
import telegram
from datetime import datetime

# ←←← SOSTITUISCI QUI I TUOI DATI ←←←
BOT_TOKEN = '7969789752:AAFxPcu7Ni1r0dRKA796-9F_BMLv9P59fbA'
CHAT_ID = '-4925344956'
bot = telegram.Bot(token=BOT_TOKEN)

def get_rtp():
    url = 'https://www.casino.org/casinoscores/it/crazy-time/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Cerca RTP nel testo (adatta dopo test)
        texts = soup.get_text()
        import re
        rtp_match = re.search(r'(\d+(?:,\d+)?)%', texts)
        if rtp_match:
            rtp_value = float(rtp_match.group(1).replace(',', '.'))
            return rtp_value
        return None
    except:
        return None

def check_alert():
    rtp = get_rtp()
    if rtp and rtp < 68:
        message = f"🚨 RTP CRAZY TIME SOTTO 68%! {rtp}% - {datetime.now().strftime('%H:%M')}"
        bot.send_message(chat_id=CHAT_ID, text=message)
        print(message)

schedule.every(5).minutes.do(check_alert)
print("Monitoraggio avviato... Ctrl+C per fermare")

while True:
    schedule.run_pending()
    time.sleep(1)
