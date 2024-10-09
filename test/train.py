import spacy


# Load the trained model
nlp = spacy.load("../models/cargo/model-best")

def predict_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Example usage
if __name__ == "__main__":
    example_text = '''
 Dear All/Oscar

 

PLEASE KINDLY PROPOSE TONNAGE FOR BELOW FIRM CARGO:

 

 

ACCT: TONGLI TIANJIN----FULLY BOOKED

DWT: SMX-UMX, MAX 20YEARS

CARGO:COAL

DELY: TO MAKE E KALI

REDELY:WCI

LAYCAN :10-16 OCT

DURATION :ABT 30 DAYS WOG

ADD COMM: 3.75%  

 

TRY 2-3LLS OR PERIOD

 

 

 

Best regards

 

MR.WANG NING/OSCAR

For and on behalf of TONGLI SHIPPING PTE.LTD

8 TEMASEK BOULEVARD #40-02，SUNTEC TOWER THREE SINGAPORE 038988

INDIA OCEAN DIVISION

Skype: wangoscar8

M.p : 18649185805

Email: tianjin1@tonglishippingpte.com

           panamax@tonglishippingpte.com
    '''
    example_text = example_text.replace('  ',' ').replace('\n','  ').replace('\t',' ').replace('  ',' ').replace('   ',' ')
    print(example_text)
    entities = predict_entities(example_text)
    print(f"Entities in '{entities}':")
    for entity in entities:
        print(f" - {entity[1]} : {entity[0]}")
