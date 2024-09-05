import spacy


# Load the trained model
nlp = spacy.load("cargo/model-best")

def predict_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Example usage
if __name__ == "__main__":
    example_text = '''
    Doc-No. 3874821   04/SEP/2024 (WED)  10:48  (+0300)  BM

 

TNS Shipbrokers and Agents Ltd (Since 1991)

phone:+359 56 841005/6, fax:+359 56 840299

home page:www.tns-shipping.com

email: chart@tns-shipping.com

 

-- / Miteva

 

Good day

 

ACC: NORTHBULK

15K / 25K DWT VSL

DEL: WCUS

REDEL: REDSEA

END SEPT

DUR: 60 DAYS +/- 10 DAYS INCHOPT

ADD COM: 3.75 PUS

 

CAN ALSO TRY VOYAGE ALL DETS AVALIBLE FOR THE NAMED TONNAGE

 

Plsd to hear

 

Kind regards,

TNS Shipbrokers - B.Miteva

 

Skype: blagovesta_bs

Mob: +359 878 593660

BIMCO Members (reg. no. 116957)

 

 
    '''
    example_text = example_text.replace('  ',' ').replace('\n','  ').replace('\t',' ').replace('  ',' ').replace('   ',' ')
    print(example_text)
    entities = predict_entities(example_text)
    print(f"Entities in '{entities}':")
    for entity in entities:
        print(f" - {entity[1]} : {entity[0]}")
