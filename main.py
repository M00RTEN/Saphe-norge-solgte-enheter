import time
import os
import requests
from threading import Thread
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from supabase import create_client

# Dummy-server for å holde Render i live
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    print(f"Starter server på port {port}...", flush=True)
    with TCPServer(("0.0.0.0", port), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

Thread(target=run_dummy_server, daemon=True).start()

# Supabase-oppsett
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

def hent_lager():
    try:
        res = requests.get(API_URL, headers=headers, timeout=20)
        if res.status_code != 200:
            print(f"API-feil: {res.status_code}", flush=True)
            return None
        
        data = res.json()
        total_lager = 0
        
        for b in data.get("filialstatus", []):
            amount_str = str(b.get("amount", "0"))
            clean_amount = amount_str.replace("+", "")
            
            if clean_amount.isdigit():
                total_lager += int(clean_amount)
                
        return total_lager
    except Exception as e:
        print(f"Skrapefeil: {e}", flush=True)
        return None

# --- NY DEL START ---
forrige_lager = None # Denne må stå her for å huske forrige måling
# --- NY DEL SLUTT ---

# Hovedløkke
while True:
    nytt_lager = hent_lager()
    if nytt_lager is not None:
        # --- NY LOGIKK FOR SALG ---
        salg = 0
        if forrige_lager is not None and nytt_lager < forrige_lager:
            salg = forrige_lager - nytt_lager
        
        try:
            # Vi sender nå variabelen 'salg' til databasen
            supabase.table('saphe_logg').insert({
                "lager": nytt_lager, 
                "solgt_siden_sist": salg
            }).execute()
            
            print(f"Suksess! Lagret {nytt_lager} stk. (Solgt siden sist: {salg})", flush=True)
            
            # Oppdater forrige_lager til det vi nettopp hentet, klar for neste runde
            forrige_lager = nytt_lager
            
        except Exception as e:
            print(f"Supabase feil: {e}", flush=True)
    
    time.sleep(120)
