import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
from telegram import Bot 
from datetime import datetime
import re

# --- CONFIGURAZIONE (Ricorda di usare le variabili d'ambiente in produzione) ---
# Usiamo i valori che hai fornito
BOT_TOKEN = "7969789752:AAFxPcu7Ni1r0dRKA796-9F_BMLv9P59fbA"
CHAT_ID = "-4925344956" 

try:
    # Inizializza il bot
    bot = Bot(token=BOT_TOKEN)
    CHAT_ID_INT = int(CHAT_ID)
except Exception as e:
    print(f"ERRORE di inizializzazione del Bot: {e}. Controlla Token e CHAT_ID.")
    # In un ambiente di produzione, potresti voler uscire o ritentare qui.
    
# --- FUNZIONI ---
def get_rtp():
    """Estrae il valore RTP usando una regex robusta sul testo del widget."""
    url = 'https://www.casino.org/casinoscores/it/crazy-time/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Inizio la richiesta per l'RTP...")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Errore HTTP: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Trova il contenitore degli stats, usando il data-testid fisso
        header_stats = soup.find('span', {'data-testid': 'bet-tracker-widget-header-stats'})
        
        if header_stats:
            # 2. Prendi tutto il testo dal contenitore
            text = header_stats.get_text(strip=True)
            
            # 3. Utilizza la regex per cercare la stringa "RTP" seguita da un numero con %
            # Pattern: (RTP\s*) -> cerca "RTP "
            # (\d+[.,]?\d*) -> cattura il numero (es. 98.63)
            # % -> seguito dal simbolo di percentuale
            rtp_match = re.search(r'RTP\s*(\d+[.,]?\d*)%', text)

            if rtp_match:
                # Il gruppo 1 contiene solo il numero
                rtp_value_str = rtp_match.group(1).replace(',', '.')
                rtp_value = float(rtp_value_str)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ RTP trovato con regex: {rtp_value}%")
                return rtp_value
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Regex fallita nel testo: {text}")
                return None
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Elemento HTML 'bet-tracker-widget-header-stats' non trovato (Contenitore principale mancante).")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Errore di richiesta (get_rtp): {e}")
        return None
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Errore generico (get_rtp): {e}")
        return None

def check_alert():
    """Controlla l'RTP e invia un avviso Telegram se è inferiore a 68."""
    rtp = get_rtp()
    
    if rtp is not None:
        if rtp < 105.0:
            message = f"🚨 **ALERT! RTP CRAZY TIME SOTTO 68%**! Attuale: **{rtp}%** - {datetime.now().strftime('%H:%M')}"
            try:
                # Se l'inizializzazione del bot è fallita, questa linea fallirà.
                # Per sicurezza uso il parse_mode Markdown per grassettare il testo.
                bot.send_message(chat_id=CHAT_ID_INT, text=message, parse_mode='Markdown')
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ALERT TELEGRAM INVIATO: {message}")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Errore nell'invio del messaggio Telegram: {e}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] RTP OK: {rtp}%")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Impossibile recuperare l'RTP (vedi log precedente).")

# --- SCHEDULAZIONE E AVVIO ---

schedule.every(1).minutes.do(check_alert)
print("--- Monitoraggio RTP avviato ---")
print(f"Chat ID configurata: {CHAT_ID}")
print("Prossimo controllo tra 5 minuti...")

# Loop principale
while True:
    schedule.run_pending()
    time.sleep(1)


