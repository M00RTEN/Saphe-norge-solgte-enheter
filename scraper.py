import requests
import json
from datetime import datetime, timedelta

# Den korrekte AJAX-URL-en som spyttet ut rådataene dine
API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def hent_lager_fra_json():
    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"API feil: {res.status_code}")
            return None
            
        # Siden Thansen returnerer ren JSON, bruker vi res.json() i stedet for tekstsøk
        data = res.json()
        
        # Vi går gjennom hver butikklinje og summerer verdien i feltet 'antal'
        total = 0
        for butikk in data:
            if "antal" in butikk:
                total += int(butikk["antal"])
                
        print(f"Suksess! Summerte opp totalt {total} stk på lager i Norge.")
        return total
            
    except Exception as e:
        print(f"Feil ved parsing av JSON: {e}")
        return None

# Last inn eksisterende historikk
try:
    with open("data.json", "r") as f:
        historikk = json.load(f)
except:
    historikk = []

naa_tid = datetime.now() + timedelta(hours=2) # Justering for norsk tidssone på GitHub
naa_streng = naa_tid.strftime("%Y-%m-%d %H:%M")
nytt_lager = hent_lager_fra_json()

# Lagre kun hvis vi fikk et gyldig tall
if nytt_lager is not None and nytt_lager > 0:
    solgt_siden_sist = 0
    if historikk:
        forrige_lager = historikk[-1]["lager"]
        if nytt_lager < forrige_lager:
            solgt_siden_sist = forrige_lager - nytt_lager
            
    historikk.append({
        "tidspunkt": naa_streng,
        "lager": nytt_lager,
        "solgt_siden_sist": solgt_siden_sist
    })
    
    historikk = historikk[-100:]
    
    with open("data.json", "w") as f:
        json.dump(historikk, f, indent=4)
    print(f"Logget suksessfullt: {nytt_lager} stk totalt.")
else:
    print("Ingen oppdatering gjort på grunn av manglende eller tomme data.")
