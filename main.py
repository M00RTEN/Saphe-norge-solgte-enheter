import time
import os
import sys
import requests
from bs4 import BeautifulSoup
from threading import Thread
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from supabase import create_client, Client

# =====================================================================
# 1. Tving Render til å lyse grønt (Web Service trikset)
# =====================================================================
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

# =====================================================================
# 2. Konfigurasjon av Supabase
# =====================================================================
# Bytt ut med dine egne detaljer hvis du ikke bruker miljøvariabler (os.environ)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "DIN_SUPABASE_URL_HER")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "DIN_SUPABASE_KEY_HER")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Koblet til Supabase!", flush=True)
except Exception as e:
    print(f"Kunne ikke koble til Supabase: {e}", flush=True)
    sys.exit(1)

# =====================================================================
# 3. Selve skraper-loopen
# =====================================================================
print("Starter Saphe-skraperen...", flush=True)

while True:
    try:
        print("Henter data fra kilden...", flush=True)
        
        # --- DIN EGEN SKRAPE-LOGIKK HER ---
        # Eksempel på hvordan du henter verdien din:
        # url = "https://www.saphe.no/..."
        # response = requests.get(url)
        # soup = BeautifulSoup(response.text, 'html.parser')
        # lager_tall = int(soup.find(id="lager-status").text)
        
        lager_tall = 0  # <--- BYTT UT DENNE med variabelen som faktisk har tallet ditt!
        
        # Print ut verdien i loggen så vi ser hva den faktisk fant:
        print(f"--> Skraperen fant denne verdien: {lager_tall}", flush=True)
        
        print("Prøver å sende tall til Supabase...", flush=True)
        
        # --- DIN SUPABASE INSERT-KODE HER ---
        # data = {"lagerbeholdning": lager_tall}
        # supabase.table('DIN_TABELL_NAVN').insert(data).execute()
        
        print("Suksess! Data sendt.", flush=True)
        
    except Exception as e:
        print(f"!!! FEIL I LOOPEN: {e}", flush=True)
        
    # Vent 30 sekunder før neste sjekk
    time.sleep(30)
