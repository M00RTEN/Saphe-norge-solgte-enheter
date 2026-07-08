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
    with TCPServer(("0.0.0.0", port), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

Thread(target=run_dummy_server, daemon=True).start()

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"
headers = {"User-Agent": "Mozilla/5.0"}

def hent_lager():
    try:
        res = requests.get(API_URL, headers=headers, timeout=20)
        data = res.json()
        total = 0
        for b in data.get("filialstatus", []):
            clean = str(b.get("amount", "0")).replace("+", "")
            if clean.isdigit(): total += int(clean)
        return total
    except: return None

forrige_lager = None

while True:
    nytt = hent_lager()
    if nytt is not None:
        salg = 0
        if forrige_lager is not None and nytt < forrige_lager:
            salg = forrige_lager - nytt
        
        try:
            supabase.table('saphe_logg').insert({"lager": nytt, "solgt_siden_sist": salg}).execute()
            print(f"Suksess! Lagret {nytt} stk. (Solgt siden sist: {salg})", flush=True)
            forrige_lager = nytt
        except Exception as e: print(f"Feil: {e}", flush=True)
    
    time.sleep(30) # Sjekker hvert 30. sekund
