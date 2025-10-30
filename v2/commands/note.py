import sqlite3
from datetime import datetime
from core.voice import speaker
import time
import spacy

nlp = spacy.load("en_core_web_sm")

connection = sqlite3.connect('notes.db', check_same_thread=False)
cursor = connection.cursor()

current_datetime = datetime.now()

def extractContent(content):
    doc = nlp(content)
    # Remove root head
    root = [token for token in doc if token.head == token][0]

    content_tokens = []
    for token in doc:
        if token.dep_ in ("ccomp", "xcomp", "dobj", "attr", "pobj") and token.head == root:
            subtree = list(token.subtree)
            content_tokens = [t.text for t in subtree]
            break
    if not content_tokens:
        content_tokens = [t.text for t in doc if t.i > 1]

    return " ".join(content_tokens)

def createTable():
    createTable = """
    CREATE TABLE IF NOT EXISTS notes (note_number INTEGER PRIMARY KEY, date TEXT, content TEXT)"""
    cursor.execute(createTable)

def getNextNoteNumber():
    cursor.execute("SELECT MAX(note_number) FROM notes")
    result = cursor.fetchone()[0]
    return 1 if result is None else result + 1

def addNote(command):
    note_number = getNextNoteNumber()
    content = extractContent(command)
    cursor.execute("INSERT INTO notes (note_number, date, content) VALUES (?, ?, ?)", (note_number, current_datetime.strftime('%m/%d/%y'), content))
    speaker.yap(f"Note {note_number} added: {content}")
    connection.commit()

def retrieveToday():
    cursor.execute("SELECT * FROM notes WHERE date = ?", (current_datetime.strftime('%m/%d/%y'),))
    notes = cursor.fetchall()
    if not notes:
        speaker.yap("No notes found from today.")
        return
    for note in notes:
        note_number, date, content = note
        speaker.yap(f"{len(notes)} from today. Note {note_number}, {content}")
        time.sleep(1)