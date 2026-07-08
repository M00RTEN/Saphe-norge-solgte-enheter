import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta

URL = "https://www.thansen.no/bil/utstyr/elutstyr/trafikkalarmer-fartskontroll/saphe-t-starter-pack-inkl.-6-mdr./n1096313/pn1545773"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def hent_lager():
    try:
        res = requests.get(URL, headers=headers)
        if res.status_code != 200: return None
        soup = BeautifulSoup(res.content, 'html.parser')
        options = soup.find_all('option')
        total = 0
        for opt in options:
            match = re.search(r"\((?:\+)?(\d+)\s*stk\.\)", opt.get_text())
            if match:
                total += int(match.group(1))
        return total
    except:
        return None

# Last inn eksisterende historikk eller opprett ny
try:
    with open("data.json", "r") as f:
        historikk = json.load(f)
except:
    historikk = []

naa_tid = datetime.now() + timedelta(hours=2) # Juster for norsk tidssone på GitHub-serveren
naa_streng = naa_tid.strftime("%Y-%m-%d %H:%M")
nytt_lager = hent_lager()

if nytt_lager is not None:
    # Regn ut salg hvis vi har tidligere data
    solgt_siden_sist = 0
    if historikk:
        forrige_lager = historikk[-1]["lager"]
        if nytt_lager < forrige_lager:
            solgt_siden_sist = forrige_lager - nytt_lager
    
    # Lagre datapunkt
    historikk.append({
        "tidspunkt": naa_streng,
        "lager": nytt_lager,
        "solgt_siden_sist": solgt_siden_sist
    })
    
    # Hold historikken til de siste 100 målingene så filen ikke blir enorm
    historikk = historikk[-100:]
    
    with open("data.json", "w") as f:
        json.dump(historikk, f, indent=4)
    print(f"Logget: {nytt_lager} på lager. Solgt siden sist: {solgt_siden_sist}")
