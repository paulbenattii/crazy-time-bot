import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
from telegram import Bot # Assicurati di aver installato python-telegram-bot (pip install python-telegram-bot)
from datetime import datetime
import re

# --- CONFIGURAZIONE ---

# Legge le variabili d'ambiente di Railway. 
# ASSICURATI che queste variabili siano impostate correttamente
# nel tuo ambiente Railway.
# Visto che hai messo valori hardcoded, li userò direttamente qui
# ma il modo corretto per ambienti di produzione è usare os.getenv().

# BOT_TOKEN = os.getenv("BOT_TOKEN") 
# CHAT_ID = os.getenv("CHAT_ID")

# Se non stai usando variabili d'ambiente in Railway, usa i valori diretti:
BOT_TOKEN = "7969789752:AAFxPcu7Ni1r0dRKA796-9F_BMLv9P59fbA"
CHAT_ID = "-4925344956" # Assicurati che questo sia un INT o una stringa che rappresenta l'ID

# Inizializza il bot
try:
    # Telegram Bot API richiede un token valido per l'inizializzazione
    bot = Bot(token=BOT_TOKEN)
    # Converto CHAT_ID in intero per essere sicuro
    CHAT_ID = int(CHAT_ID)
except Exception as e:
    print(f"ERRORE di inizializzazione del Bot: {e}")
    # Considera di uscire se il bot non può essere inizializzato.
    # exit(1)

# --- FUNZIONI ---

def get_rtp():
    """Estrae il valore RTP dal tag specifico del sito."""
    url = 'https://www.casino.org/casinoscores/it/crazy-time/'
    # Un User-Agent è sempre una buona pratica
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    print("Inizio la richiesta per l'RTP...")

    try:
        response = requests.get(url, headers=headers)
        # Controlla se la richiesta è andata a buon fine
        if response.status_code != 200:
            print(f"Errore HTTP: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Trova l'elemento specifico usando le classi CSS
        # <p class="font-bold p-0 m-0 flex text-xs xxs:text-[15px]">
        rtp_element = soup.find('p', class_='font-bold p-0 m-0 flex text-xs xxs:text-[15px]')

        if rtp_element:
            # Estrae tutto il testo all'interno del tag
            text = rtp_element.get_text(strip=True)
            # Cerca il valore numerico con la percentuale
            # Il pattern cerca un numero (con o senza virgola/punto) seguito da %
            rtp_match = re.search(r'(\d+[.,]?\d*)%', text)

            if rtp_match:
                # Prende il valore e sostituisce la virgola con il punto per float()
                rtp_value_str = rtp_match.group(1).replace(',', '.')
                rtp_value = float(rtp_value_str)
                print(f"RTP trovato: {rtp_value}%")
                return rtp_value
            else:
                print("Regex non ha trovato il pattern RTP nel testo:", text)
                return None
        else:
            print("Elemento HTML specifico non trovato.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Errore di richiesta (get_rtp): {e}")
        return None
    except Exception as e:
        print(f"Errore generico (get_rtp): {e}")
        return None

def check_alert():
    """Controlla l'RTP e invia un avviso se è inferiore a 68."""
    print(f"Esecuzione di check_alert alle {datetime.now().strftime('%H:%M:%S')}...")
    rtp = get_rtp()
    
    if rtp is not None:
        if rtp < 105:
            message = f"🚨 RTP CRAZY TIME SOTTO 68%! **{rtp}%** - {datetime.now().strftime('%H:%M')}"
            try:
                # Uso parse_mode='Markdown' per enfatizzare l'RTP
                bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
                print(f"ALERT INVIATO: {message}")
            except Exception as e:
                print(f"Errore nell'invio del messaggio Telegram: {e}")
        else:
            print(f"RTP OK: {rtp}%")
    else:
        print("Impossibile recuperare l'RTP.")

# --- SCHEDULAZIONE E AVVIO ---

# Ogni 5 minuti
schedule.every(1).minutes.do(check_alert)
print("--- Monitoraggio RTP avviato ---")
print(f"Bot Token: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:]}") # Stampa parziale per sicurezza
print(f"Chat ID: {CHAT_ID}")

# Loop principale
while True:
    schedule.run_pending()
    time.sleep(1)

