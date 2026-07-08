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
        # Lagt til timeout=10 for å unngå at skriptet henger hvis Thansen er nede
        res = requests.get(API_URL, headers=headers, timeout=10)
        if res.status_code != 200:
            return None
        data = res.json()
        total_lager = 0
        for b in data.get("filialstatus", []):
            clean_amount = str(b.get("amount", "0")).replace("+", "")
            if clean_amount.isdigit():
                total_lager += int(clean_amount)
        return total_lager
    except Exception as e:
        print(f"Skrapefeil: {e}", flush=True)
        return None

# Hukommelse for forrige lager
forrige_lager = None

# Hovedløkke
print("Starter hovedløkke...", flush=True)
while True:
    nytt_lager = hent_lager()
    
    if nytt_lager is not None:
        salg = 0
        # Hvis vi har et forrige lager og det nye er mindre, har vi salg
        if forrige_lager is not None and nytt_lager < forrige_lager:
            salg = forrige_lager - nytt_lager
        
        try:
            # Send til Supabase
            supabase.table('saphe_logg').insert({
                "lager": nytt_lager, 
                "solgt_siden_sist": salg
            }).execute()
            
            print(f"Suksess! Lagret {nytt_lager} stk. (Solgt siden sist: {salg})", flush=True)
            
            # Oppdater hukommelsen KUN hvis vi fikk lagret
            forrige_lager = nytt_lager
            
        except Exception as e:
            print(f"Supabase feil: {e}", flush=True)
    else:
        print("Kunne ikke hente lager, prøver igjen om 30 sek...", flush=True)
    
    # Kortere ventetid for å fange opp salg raskere
    time.sleep(30)
