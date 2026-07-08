import time
import os
import requests
from threading import Thread
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from supabase import create_client, Client

# 1. Dummy-server (Holder Render "Live")
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = TCPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_dummy_server, daemon=True).start()

# 2. Supabase-oppsett
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Skrape-konfigurasjon
API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"
headers = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

def hent_lager_fra_json():
    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        data = res.json()
        return sum(int(butikk.get("antal", 0)) for butikk in data)
    except Exception as e:
        print(f"Feil ved henting: {e}", flush=True)
        return None

# 4. Hoved-loop
print("Starter skraper...", flush=True)
while True:
    nytt_lager = hent_lager_fra_json()
    
    if nytt_lager is not None:
        print(f"--> Skraperen fant: {nytt_lager} stk", flush=True)
        
        # Send til Supabase (Bytt ut 'lager_tabell' med navnet på din tabell i Supabase)
        try:
            supabase.table('lager_tabell').insert({
                "lager": nytt_lager
            }).execute()
            print("Suksess! Data sendt til Supabase.", flush=True)
        except Exception as e:
            print(f"!!! Feil ved sending til Supabase: {e}", flush=True)
    
    time.sleep(30)
