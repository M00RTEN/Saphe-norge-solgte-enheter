import requests
import re
import json
from datetime import datetime, timedelta

URL = "https://www.thansen.no/bil/utstyr/elutstyr/trafikkalarmer-fartskontroll/saphe-t-starter-pack-inkl.-6-mdr./n1096313/pn1545773"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "no,nb;q=0.9,en;q=0.8"
}

def hent_lager():
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        if res.status_code != 200: 
            print(f"Feil statuskode: {res.status_code}")
            return None
        
        # Thansen dytter ofte butikkbeholdningen inn i et JavaScript-objekt på siden.
        # Vi søker bredere etter mønstre som "(X stk.)" eller "+25 stk." i hele teksten.
        tekst = res.text
        funn = re.findall(r"\((?:\+)?(\d+)\s*stk\.\)", tekst)
        
        if funn:
            # Summerer opp alle tallene vi finner i parentesene
            total = sum(int(antall) for antall in funn)
            # Hvis tallet blir ekstremt høyt fordi den teller andre ting, halverer vi det ikke, 
            # men her luker vi ut dubletter hvis de listes to ganger på siden.
            print(f"Fant {len(funn)} butikklinjer. Totalt funnet: {total}")
            return total
            
        print("Fant ingen treff med RegEx.")
        return None
    except Exception as e:
        print(f"Scraping feilet: {e}")
        return None

# Last inn historikk
try:
    with open("data.json", "r") as f:
        historikk = json.load(f)
except:
    historikk = []

naa_tid = datetime.now() + timedelta(hours=2)
naa_streng = naa_tid.strftime("%Y-%m-%d %H:%M")
nytt_lager = hent_lager()

# Hvis den returnerer 0 eller None, vil vi ikke overskrive med feil data hvis vi har gammel data
if nytt_lager forrige_lager = historikk[-1]["lager"] if historikk else 0

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
    print(f"Logget suksessfullt: {nytt_lager}")
else:
    print("Kunne ikke oppdatere lager, beholder eksisterende data.")
