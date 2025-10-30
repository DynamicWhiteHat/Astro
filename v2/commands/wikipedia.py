import wikipediaapi
import spacy
from core.voice import speaker
from core.nounTransformer import return_topic


wiki_wiki = wikipediaapi.Wikipedia(user_agent='Astro', language='en')
nlp = spacy.load("en_core_web_sm")

def return_summary(command, ui):
    topic = return_topic(command)
    print(topic)
    page_py = page_py = wiki_wiki.page(topic)
    doc = nlp(page_py.summary)
    sentences = list(doc.sents)
    first2 = sentences[:2]
    sentences = " ".join([sent.text.strip() for sent in first2])
    print("Page - Summary: %s" % sentences)
    try:
        ui.showResponseTextSignal.emit(sentences)
        speaker.yap(sentences)
    except:
        ui.showResponseTextSignal.emit("Sorry, there was an error processing your request.")
        speaker.yap("Sorry, there was an error processing your request.")