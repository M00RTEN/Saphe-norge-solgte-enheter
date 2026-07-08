import time
import os
import requests
from threading import Thread
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from supabase import create_client, Client

# Dummy-server
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = TCPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_dummy_server, daemon=True).start()

# Supabase-oppsett
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"
headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.thansen.no/"}

def hent_lager():
    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        data = res.json()
        # Dataene ligger under "filialstatus"
        butikker = data.get("filialstatus", [])
        return sum(int(b.get("antal", 0)) for b in butikker)
    except Exception as e:
        print(f"Feil: {e}", flush=True)
        return None

while True:
    nytt_lager = hent_lager()
    if nytt_lager is not None:
        try:
            # Sender til Supabase
            supabase.table('saphe_logg').insert({"lager": nytt_lager, "solgt_siden_sist": 0}).execute()
            print(f"Suksess! Logget {nytt_lager} stk.", flush=True)
        except Exception as e:
            print(f"!!! Supabase feil: {e}", flush=True)
    time.sleep(60)
