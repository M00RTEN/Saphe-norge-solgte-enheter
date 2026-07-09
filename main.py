import time
import os
import requests
import random  # Lagt til for tilfeldig intervall
from datetime import datetime, timedelta, UTC  # Lagt til UTC for moderne tidsberegning
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

# Henter den siste reelle lagret-verdien uansett tidsrom for å bruke som sammenligningsgrunnlag
def hent_siste_gyldige_lager():
    try:
        response = (
            supabase.table("saphe_logg")
            .select("lager")
            .gt("lager", 0)  # Sikrer at vi ikke henter rader der Thansen har hikket (0)
            .order("tidspunkt", desc=True)  # Sorterer med nyeste tidsstempel først
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]["lager"]
    except Exception as e:
        print(f"Kunne ikke hente siste lager fra database: {e}", flush=True)
    return None

def hent_lager():
    try:
        # Lagt til timeout=10 for å unngå at skriptet henger hvis Thansen is nede
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

# Hovedløkke
print("Starter hovedløkke...", flush=True)
while True:
    nytt_lager = hent_lager()
    
    # Sjekk så vi skipper runden om Thansen gir oss 0 eller ingenting ved en feil
    if nytt_lager is not None and nytt_lager > 0:
        salg = 0
        
        # Henter historikk (siste lagret rad)
        forrige_lager_db = hent_siste_gyldige_lager()
        
        if forrige_lager_db is not None:
            if nytt_lager < forrige_lager_db:
                # REELT SALG
                salg = forrige_lager_db - nytt_lager
                print(f"SALG OPPDAGET! Solgt siden sist: {salg}", flush=True)
            elif nytt_lager > forrige_lager_db:
                # REELT PÅFYLL (Lageret har økt)
                paafyll = nytt_lager - forrige_lager_db
                print(f"LAGERPÅFYLL OPPDAGET! Økning på: +{paafyll} stk. Nytt utgangspunkt: {nytt_lager}", flush=True)
                salg = 0  # Ingen salg på denne spesifikke raden
            else:
                # Ingen endring i lageret
                salg = 0
        else:
            # Hvis databasen er helt tom (første kjøring)
            salg = 0
        
        try:
            # Send til Supabase
            supabase.table('saphe_logg').insert({
                "lager": nytt_lager, 
                "solgt_siden_sist": salg
            }).execute()
            
            print(f"Suksess! Lagret {nytt_lager} stk. til databasen.", flush=True)
            
            # Automatisk 31-dagers renhold
            try:
                tidsgrense = (datetime.now(UTC) - timedelta(days=31)).isoformat()
                supabase.table("saphe_logg").delete().lt("tidspunkt", tidsgrense).execute()
            except Exception as e:
                print(f"Kunne ikke slette gamle data: {e}", flush=True)
                
        except Exception as e:
            print(f"Supabase feil: {e}", flush=True)
            
    elif nytt_lager == 0:
        print("Thansen rapporterer 0 i lager (feil/api-timeout), hopper over denne runden...", flush=True)
    else:
        print("Kunne ikke hente lager, prøver igjen snart...", flush=True)
    
    # Tilfeldig pause mellom 1 og 2 minutter (60-120 sekunder)
    pause = random.randint(60, 120)
    print(f"Venter i {pause} sekunder før neste sjekk...", flush=True)
    time.sleep(pause)
