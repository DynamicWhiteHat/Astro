import spacy

nlp = spacy.load("en_core_web_sm")

def return_topic(text):
    doc = nlp(text)

    filtered_chunks = []
    for chunk in doc.noun_chunks:
        words = [token.text for token in chunk if not token.is_stop and token.is_alpha]
        if words:
            filtered_chunks.append(" ".join(words))

    if filtered_chunks:
        topic = filtered_chunks[-1]
    else:
        topic = " ".join([token.text for token in doc if not token.is_stop and token.is_alpha])
    return topic