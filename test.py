import spacy
import requests
# Load the trained model
nlp = spacy.load("../models/vessel_info/model-best")

url = "http://127.0.0.1:8000/predict/tonnage"

def predict_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def predit_entities_api(text):
    response = requests.post(url, json={"text": text})
    print(response.status_code)
    if response.status_code == 200:
        return response.json()['entities']
    else:
        return response.text


# Example usage
if __name__ == "__main__":
    example_text = '''

FROM: ARYACORP PVT. LTD.
DATE & TIME: 07-10-2024 18:32:59   (GMT +5:30)
REFERΕNCE NO: 17963979 


ATTN CHARTERING DESK
DEAR SIR
GOOD DAY
DIRECT OWNERS VESSEL
PLEASE ADVISE SUITABLE CARGO FOR BELOW VESSEL

/// DO NOT RE-CIRCULATE ///

MV NBA PROSPERITY - SMX - OPEN BEIRA - 25-30 OCT 2024 AGW
BROB abt 750 mts VLSFO / abt 20 mts LSMGO 
Can try any direction. 
MV NBA Prosperity
Bulk Carrier
Built: 2010
Liberia Flag,
Class: LR
Deadweight/Draft: 56,907.13 MT (summer) on 12.80 M (summer) / TPC : 58.80 MT
GRT/NRT: 33,044 / 19,231
LOA: 189.99 M / LBP: 185.00 M / Beam: 32.26 M
HO/HA – 5/5
Grain: 71,634.10 cubic meter
Hatch Dimensions:
Hatch #1: 18.86 x 18.26 m
Hatch #2, #3, #4, #5: 21.32 x 18.26 m
Hatch Covers: hydraulic/folding
Hold Dimensions:
Hold #1: 27.85 x 23.82 x 20.50 m
Hold #2/4: 28.70 x 23.82 x 20.30 m
Hold #3: 27.06 x 23.82 x 20.30 m
Hold #5: 27.05 x 23.82 x 20.30 m
CARGO HOLDS CO2 FITTED.
Tank Top Strength: No. 1,3,5 – 25 t/m2, No. 2,4 – 20 t/m2,
Deck – 1 t/m2, Hatch covers – 2.3 t/m2
Cargo Gear : Cranes: 4 x 30 Tons
Grabs : 4 remote electro hydraulic. Lifting capacity – 6-12 M3
Speed and Consumption
Ballast: about 12.5 knots on about 25 mt VLSFO and about 0.2 mt LSGO
Laden: about 12 knots on about 26 mt VLSFO and about 0.2 mt LSGO
Consumption in Port –
Gear working: about 5 mt VLSFO + abt 0.2 mt LSGO
Idle: about 3 mt VLSFO + abt 0.2 mt LSGO
ADA 


PLSD TO HEAR.
 
BEST REGARDS,

TONNAGE DESK:

PG-WCI-ECI-SEAS: 
Carlton Carlo | Mob: +91 9311 255657  | Skype: cid.971bb208b4e2c3bb
Arjun Chaudhary | Mob: +91 9311 255656 | Skype: live:.cid.d66bb9d9c752a104 

FEAST- SCHINA :
Nitin Sharma | Mob: +91 9311 255654  | Skype: mailto:acpl.nitindev@outlook.com
 
AS BROKERS ONLY
As Agents for Core Shipping Ltd.
Email: mailto:fix@aryacorp.com (Chartering) |  mailto:ops@aryacorp.com (Post Fixture)
Follow us on LinkedIn: https://www.linkedin.com/company/arya-corp-private-limited
Website: https://www.aryacorp.com
SHIPBROKING | BUNKERING | AGENCY & REPRESENTATION
    '''
    example_text = example_text.replace('  ', ' ').replace('\n', '  ').replace('\t', ' ').replace('  ', ' ').replace(
        '   ', ' ')
    print(example_text)
    # entities = predict_entities(example_text)
    # print(f"Entities in '{entities}':")
    # for entity in entities:
    #     print(f" - {entity[1]} : {entity[0]}")
    for row in predit_entities_api(example_text):
        print(f" - {row['label']} : {row['text']}")
