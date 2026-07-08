import requests
import re
import json
from datetime import datetime, timedelta

# Vi bruker endepunktet du fant i Network-fanen som henter status for ALLE butikker på varen
API_URL = "https://www.thansen.no/ajax/functionGetInstockStatus.asp?pn=1545773"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def hent_lager_fra_api():
    try:
        res = requests.get(API_URL, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"API feil: {res.status_code}")
            return None
            
        tekst = res.text
        # API-et returnerer rå HTML-struktur for rullegardinmenyen.
        # Vi bruker RegEx til å trekke ut alle tallene som står som "X stk." eller "+25 stk."
        funn = re.findall(r"\((?:\+)?(\d+)\s*stk\.\)", tekst)
        
        if funn:
            # Summerer opp beholdningen fra alle butikkene i hele Norge
            total = sum(int(antall) for antall in funn)
            print(f"Suksess! Fant {len(funn)} butikker. Totalt på lager i Norge: {total}")
            return total
            
        print("Klarte ikke å lese tall ut fra API-responsen.")
        return None
    except Exception as e:
        print(f"Feil ved henting av API: {e}")
        return None

# Last inn eksisterende historikk
try:
    with open("data.json", "r") as f:
        historikk = json.load(f)
except:
    historikk = []

naa_tid = datetime.now() + timedelta(hours=2) # Justering for norsk tidssone på GitHub-serveren
naa_streng = naa_tid.strftime("%Y-%m-%d %H:%M")
nytt_lager = hent_lager_fra_api()

# Sørg for at vi kun lagrer hvis vi faktisk fikk et gyldig tall over 0
if nytt_lager is not None and nytt_lager > 0:
    solgt_siden_sist = 0
    if historikk:
        forrige_lager = historikk[-1]["lager"]
        # Hvis lageret har sunket, har vi et salg!
        if nytt_lager < forrige_lager:
            solgt_siden_sist = forrige_lager - nytt_lager
            
    historikk.append({
        "tidspunkt": naa_streng,
        "lager": nytt_lager,
        "solgt_siden_sist": solgt_siden_sist
    })
    
    # Bevar de 100 siste målingene
    historikk = historikk[-100:]
    
    with open("data.json", "w") as f:
        json.dump(historikk, f, indent=4)
    print(f"Logget til data.json: {nytt_lager} stk på lager.")
else:
    print("Ingen oppdatering gjort (ugyldig eller tomt lagertall).")
