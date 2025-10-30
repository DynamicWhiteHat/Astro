from AppOpener import open, close
from core.voice import speaker
import spacy

nlp = spacy.load("en_core_web_sm")


def parseWords(m_input):
    doc = nlp(m_input)
    nouns = []   
    custom = ["ai", "youtube"]
    named_entities = {ent.text for ent in doc.ents}
    custom_entities = {"Microsoft Edge", "Steelseries GG", "File Explorer"}
    named_entities.update(custom_entities)

    for token in doc:
        if token.text in named_entities:
            nouns.append(token.text)
        elif token.pos_ == "PROPN" or token.text.lower() in custom or token.pos_ == "NOUN":
            nouns.append(token.text)
    return nouns


def processApp(command):
    apps = parseWords(command)
    if "open" in command.lower():
        for app in apps:
            try:
                open(app, match_closest=True)
            except Exception as e:
                print(e)
    elif "close" in command.lower():
        for app in apps:
            try:
                close(app, match_closest=True)
            except Exception as e:
                print(e)

    