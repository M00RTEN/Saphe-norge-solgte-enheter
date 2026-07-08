import time
import requests
import os
from supabase import create_client, Client
from datetime import datetime

API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"

# Render henter disse trygt fra miljøvariablene vi setter etterpå
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Mangler Supabase-nøkler i miljøvariablene!")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

print("Sky-skraper startet! Kjører hvert 30. sekund...")

while True:
    try:
        res = requests.get(API_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            nytt_lager = sum(int(butikk["antal"]) for butikk in data if "antal" in butikk)

            if nytt_lager > 0:
                # Sjekk forrige måling i Supabase
                forrige = supabase.table("saphe_logg").select("lager").order("id", desc=True).limit(1).execute()
                
                solgt_siden_sist = 0
                if forrige.data:
                    forrige_lager = forrige.data[0]["lager"]
                    if nytt_lager < forrige_lager:
                        solgt_siden_sist = forrige_lager - nytt_lager

                # Lagre i Supabase
                supabase.table("saphe_logg").insert({
                    "lager": nytt_lager,
                    "solgt_siden_sist": solgt_siden_sist
                }).execute()

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Supabase oppdatert: {nytt_lager} stk.")
        else:
            print(f"Feil fra Thansen: {res.status_code}")

    except Exception as e:
        print(f"Feil i loopen: {e}")

    # Her bestemmer du intervallet i sekunder (30 sekunder)
    time.sleep(30)
