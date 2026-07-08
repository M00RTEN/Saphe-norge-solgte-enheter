import time
import os
import sys
from threading import Thread
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
# ... dine eksisterende imports her (requests, supabase, bs4 osv.) ...

# 1. Tving Render til å lyse grønt (Web Service trikset)
def run_dummy_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = TCPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
        print(f"Dummy-server startet på port {port}", flush=True)
        server.serve_forever()
    except Exception as e:
        print(f"Dummy-server feilet: {e}", flush=True)

# Start serveren i bakgrunnen umiddelbart
Thread(target=run_dummy_server, daemon=True).start()

# 2. Selve skraper-loopen din
print("Starter Saphe-skraperen...", flush=True)

while True:
    try:
        print("Henter data fra kilden...", flush=True)
        
        # --- HER SKAL DIN EGEN SKRAPE-LOGIKK LIGGE ---
        # Pass på at variablene dine dytter RIKTIG tall inn til Supabase.
        # F.eks. hvis du har: lager_tall = sjekk_saphe()
        
        print("Prøver å sende tall til Supabase...", flush=True)
        
        # --- DIN SUPABASE INSERT KODE HER ---
        # f.eks: supabase.table('lager').insert({...}).execute()
        
        print("Suksess! Data sendt.", flush=True)
        
    except Exception as e:
        print(f"!!! FEIL I LOOPEN: {e}", flush=True)
        
    time.sleep(30)
