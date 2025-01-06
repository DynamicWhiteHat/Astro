from sentence_transformers import SentenceTransformer
import webbrowser 
import speech_recognition as sr
from AppOpener import open, close
import spacy
import inspect
import requests
import os
from functools import partial
import torch
from ollama import generate
from groq import Groq
from TTS.api import TTS
import sounddevice as sd
import cv2
import base64
import keyboard
from dotenv import load_dotenv
from datetime import datetime
import time
import threading
from googletrans import Translator


# Suppress the specific warning
#warnings.filterwarnings("ignore", category=UserWarning, message=".*torch.load.*")

load_dotenv()

#cv2 setup

cam = cv2.VideoCapture(0)

#TTS setup
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)

#Groq set up:
client = Groq(
    api_key=os.getenv("GROQ"),
)

audio = "audio.wav"

def sayAudio(text):
    wav = tts.tts(text, speaker_wav=audio, language="en")
    sd.play(wav, samplerate=23500)
    sd.wait()

def stream_callback(token):
    print(token, end='', flush=True)

#Pixabay API key   
api_key = os.getenv("PIXABAY")

#Set up speech to text
r = sr.Recognizer()

#Sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

#spacy model
nlp = spacy.load("en_core_web_sm")

#languages
language_map = {
    'Afrikaans': 'af',
    'Albanian': 'sq',
    'Amharic': 'am',
    'Arabic': 'ar',
    'Armenian': 'hy',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bengali': 'bn',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Cebuano': 'ceb',
    'Chinese (Simplified)': 'zh-cn',
    'Chinese (Traditional)': 'zh-tw',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'English': 'en',
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Filipino': 'tl',
    'Finnish': 'fi',
    'French': 'fr',
    'Galician': 'gl',
    'Georgian': 'ka',
    'German': 'de',
    'Greek': 'el',
    'Gujarati': 'gu',
    'Haitian Creole': 'ht',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Indonesian': 'id',
    'Irish': 'ga',
    'Italian': 'it',
    'Japanese': 'ja',
    'Javanese': 'jw',
    'Kannada': 'kn',
    'Kazakh': 'kk',
    'Khmer': 'km',
    'Korean': 'ko',
    'Kurdish (Kurmanji)': 'ku',
    'Kyrgyz': 'ky',
    'Lao': 'lo',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Macedonian': 'mk',
    'Malay': 'ms',
    'Malayalam': 'ml',
    'Maltese': 'mt',
    'Maori': 'mi',
    'Marathi': 'mr',
    'Mongolian': 'mn',
    'Myanmar (Burmese)': 'my',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Pashto': 'ps',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Punjabi': 'pa',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Serbian': 'sr',
    'Sesotho': 'st',
    'Sinhala': 'si',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Somali': 'so',
    'Spanish': 'es',
    'Sundanese': 'su',
    'Swahili': 'sw',
    'Swedish': 'sv',
    'Tagalog': 'tl',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Thai': 'th',
    'Turkish': 'tr',
    'Ukrainian': 'uk',
    'Urdu': 'ur',
    'Uzbek': 'uz',
    'Vietnamese': 'vi',
    'Welsh': 'cy',
    'Xhosa': 'xh',
    'Yiddish': 'yi',
    'Yoruba': 'yo',
    'Zulu': 'zu'
}

def is_connected():
    try:
        # Try connecting to a reliable website
        requests.get("https://www.google.com", timeout=1.5)
        return True
    except requests.ConnectionError:
        return False

def recognize(type=2):
    #return input("response:")
    try:
        with sr.Microphone() as mic:
            r.adjust_for_ambient_noise(mic, duration=0.2)
            if type == 1:
                r.pause_threshold = 0.6
            if type == 2:
                r.pause_threshold = 1
            audio = r.listen(mic)
            if online:
                text = r.recognize_google(audio)
                while text == None:
                    text = r.recognize_google(audio)
                return text
            else:
                text = r.recognize_whisper(audio)
                while text == None:
                    text = r.recognize_whisper(audio)
                return text
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results: {e}")

def askAI():
    print("Asking AI, online status: " + str(online))
    text = recognize()  # Recognize initial command/text

    if online:
        if "take a picture" in text.lower():
            cv2.namedWindow("Take a picture")
            taking = True
            while taking:
                result, image = cam.read()  # Capture an image

                if result:  # Check if the frame was captured successfully
                    cv2.imshow("Take a picture", image)  # Display the current frame

                cv2.waitKey(1)  # Wait for 1 millisecond for key press

                if keyboard.is_pressed("space"):  # Check if the spacebar is pressed
                    taking = False  # Stop the loop if spacebar is pressed

            # Release the camera after capturing
            cam.release()
            cv2.destroyAllWindows()

            if result:
                print("What do you want to say?")
                query = recognize()  # Recognize additional query after taking a picture

                # Encode the image as PNG and convert to base64
                _, encoded_image = cv2.imencode('.png', image)
                baseImage = base64.b64encode(encoded_image).decode('utf-8')
                image_url = f"data:image/png;base64,{baseImage}"

                # Send the image and text to the AI model
                completion = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": query
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=2,
                    max_tokens=1024,
                    top_p=1,
                    stream=False,
                    stop=None,
                )

                print(completion.choices[0].message.content)
                sayAudio(completion.choices[0].message.content)

        else:
            # If no picture-taking command, proceed with regular chat completion
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                model="llama3-8b-8192",
            )
            print(chat_completion.choices[0].message.content)
            sayAudio(chat_completion.choices[0].message.content)
    else:
        fullresponse = ""
        sayAudio("You are offline, using locally available Llama 3.2. Responses may be delayed")
        for part in generate('llama3', text, stream=True):
            print(part['response'], end='', flush=True)
            fullresponse += part["response"]
        sayAudio(fullresponse)
            
def openApp(apps):
    for app in apps:
        try:
            sayAudio("Opening " + app)
            open(app, match_closest=True)
        except Exception as e:
            print(e)

def closeApp(apps):
    for app in apps:
        try:
            sayAudio("Closing " + app)
            close(app, match_closest=True)
        except Exception as e:
            print(e)

def showImage(image):
    url = f"https://pixabay.com/api/?key={api_key}&q={image}&image_type=photo&pretty=true&per_page=5"
    response = requests.get(url)
    json_data = response.json()
    try:
        for image in json_data['hits']:
            i = image['largeImageURL']
            webbrowser.open(i)
    except:
        print("error")

def browse(url):
    try:
        for link in url:
            webbrowser.open(f"www.{link}.com")
    except Exception as e:
        print(e)

def search(query):
    term = ', '.join(query)
    webbrowser.open(f"http://google.com/search?q={term}")

def off(action_type):
    if action_type == 1:
        print("Are you sure you want to shut down?")   
        sayAudio("Are you sure you want to shut down?")        
        text = recognize()
        if "yes" in text:
            os.system('shutdown -s -t 0')
        elif "no" in text:
            print("Shut down cancelled")
            sayAudio("Shut down cancelled")
    elif action_type == 2:
        print("Are you sure you want to restart?")
        sayAudio("Are you sure you want to restart?")        
        text = recognize()
        if "yes" in text:
            os.system('shutdown -r -t 0')
        elif "no" in text:
            print("Restart cancelled")
            sayAudio("Restart cancelled")

    elif action_type == 3:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def get_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M")
    print("Current Time:", formatted_time)
    sayAudio("The time is " + str(formatted_time))

def timer():
    print("How many minutes would you like a timer for?")
    sayAudio("How many minutes would you like a timer for?")
    minutes = recognize()
    seconds = minutes*60
    timer = 0
    while timer < seconds:
        timer+=1
        time.sleep(1)
    print("Your timer is done")
    sayAudio("Your timer is done")

def start_timer(time_in_minutes):
    timer_thread = threading.Thread(target=timer, args=(time_in_minutes,))
    timer_thread.start()

def change_voice():
    global audio
    if audio == "audio.wav":
        audio = "audio2.wav" 
        sayAudio("Voice changed to Andrew")

    else:
        audio = "audio.wav"
        sayAudio("Voice changed to Evelyn")


commands = {
    "open": openApp,
    "ask": askAI,
    "exit": exit,
    "show": showImage,
    "go to": browse,
    "search": search,
    "shut down": partial(off, 1),  # Defer the a`off` call with `type=1`
    "restart": partial(off, 2),    # Defer the `off` call with `type=2`
    "sleep": partial(off, 3),      # Defer the `off` call with `type=3`
    "close": closeApp,
    "clock": get_time,
    "set timer": timer,
    "change voice": change_voice
}

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

def processCommand(m_input):
    for command, action in commands.items():
        print(command.lower() + " : " + m_input.strip().lower())
        if command.lower() == m_input.strip().lower():
            if inspect.signature(action).parameters:
                nouns = parseWords(m_input)
                return action(nouns if nouns else None)
            else:
                return action()
    nouns = parseWords(m_input)
    for command, action in commands.items():
                if command in nouns:
                    nouns.remove(command)
    for token in nouns:
        m_input = m_input.replace(token, '')
    print(m_input)
    embeddingUser = model.encode(m_input)
    for command, action in commands.items():
        embeddingCommand = model.encode(command)
        similarity = model.similarity(embeddingUser, embeddingCommand)
        print(similarity)
        if similarity > 0.6:
            print(nouns)
            # If the function takes parameters (i.e., num_params > 0), pass nouns; otherwise, call it without any parameter
            if inspect.signature(action).parameters:
                return action(nouns if nouns else None)
            else:
                return action()  # No parameters needed
    return None

print("running")

while True:
    online = is_connected()
    text = recognize(1)
    print(text)
    if text == None:
        continue
    else:
        text=text.lower()
    if "astro" in text:
        print("active")
        if text == "astro":
            print("not")
            text = recognize()
            print(text)

        else:
            print("found")
            text = text.replace("astro ", "")

        if not text:  # Check if recognize() returned None
            print("Sorry, I did not understand. Please try again.")
            continue  # Skip this iteration of the loop

        if text.lower() == "exit":
            print("Exiting program")
            break

        action = processCommand(text)
        if action:
            action()
        else:
            print("Sorry, no matching command found.")

