import time
import os
import requests
from supabase import create_client

# Supabase-oppsett
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# URL og Headers
API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.thansen.no/",
    "X-Requested-With": "XMLHttpRequest"
}

def hent_lager():
    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        # Sjekk at vi får OK svar
        if res.status_code == 200:
            data = res.json()
            butikker = data.get("filialstatus", [])
            total = sum(int(b.get("antal", 0)) for b in butikker)
            return total
        else:
            print(f"Server svarte med kode: {res.status_code}", flush=True)
            return None
    except Exception as e:
        print(f"Feil: {e}", flush=True)
        return None

print("Starter skraper...", flush=True)
while True:
    nytt_lager = hent_lager()
    
    # Send kun hvis vi fikk et tall (selv om det er 0, er det et gyldig tall fra API)
    if nytt_lager is not None:
        print(f"--> Fant {nytt_lager} stk på lager", flush=True)
        try:
            supabase.table('saphe_logg').insert({
                "lager": nytt_lager, 
                "solgt_siden_sist": 0
            }).execute()
            print("Suksess! Data sendt.", flush=True)
        except Exception as e:
            print(f"!!! Supabase feil: {e}", flush=True)
    
    time.sleep(60)
