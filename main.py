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
from customtkinter import *
import warnings
import re

# Suppress the specific warning
warnings.filterwarnings("ignore", category=UserWarning, message=".*torch.load.*")

#cv2 setup
cam = cv2.VideoCapture(0)

#TTS setup
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(device)

#Groq set up:
client = Groq(
    api_key=os.getenv("GROQ"),
)

#Pixabay API key   
api_key = os.getenv("PIXABAY")

#Set up speech to text
r = sr.Recognizer()

#Sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

#spacy model
nlp = spacy.load("en_core_web_sm")

#other
audio = "audio.wav"
online = False
load_dotenv()


#tkinter setup
def adjust_question_frame_size(event=None):
    # Adjust the height of the question frame based on the content
    content_height = question_label.winfo_height()
    max_height = 55  # Maximum height for the question frame
    new_height = min(content_height, max_height)  # Don't exceed max height
    question_frame.configure(height=new_height)

def adjust_response_frame_size(event=None):
    # Adjust the height of the response frame based on the content
    content_height = response_label.winfo_height()
    max_height = 150  # Maximum height for the response frame
    min_height = 55   # Minimum height for the response frame
    new_height = min(max(content_height, min_height), max_height)  # Adjust between min and max height
    response_frame.configure(height=new_height)

    # Also adjust the main frame height to fit the new content, without extra space at the bottom
    total_height = 55 + question_frame.winfo_height() + new_height  # 55px for question frame
    app.geometry(f"500x{total_height}")  # Adjust the window height dynamically

app = CTk()
Montserrat = CTkFont(family="Montserrat", size=12, weight="bold")
Montserrat_line = CTkFont(family="Montserrat", size=12, weight="bold", underline=True)

app.attributes('-alpha', 0.9)

app.geometry("+1290+10")
app.maxsize(width=500, height=200)
#app.overrideredirect(True) 

frame = CTkFrame(master=app, width=500, height=150)
frame.pack(fill="both", expand=True)

# Scrollable frame for the Question section
question_frame = CTkScrollableFrame(frame, width=480, height=55, fg_color="transparent")
question_frame.place(x=10, y=10)
question_frame._scrollbar.configure(height=0)
question_label = CTkLabel(master=question_frame, text="", font=Montserrat_line, text_color="#FFFFFF")
question_label.pack(pady=5, padx=5, anchor="nw")

# Scrollable frame for the Response section
response_frame = CTkScrollableFrame(master=frame, width=480, height=55, fg_color="transparent")
response_frame.place(x=10, y=75)  # Top padding of 10px + question_frame height (55) + 10px gap
response_frame._scrollbar.configure(height=0)
response_label = CTkLabel(master=response_frame, text="" * 1, font=Montserrat, text_color="#FFFFFF")
response_label.pack(pady=5, padx=5, anchor="nw")

# Adjust the question and response frame size dynamically
question_label.bind("<Configure>", adjust_question_frame_size)
response_label.bind("<Configure>", adjust_response_frame_size)

def response(text):
    print(text)
    response_label.configure(text=text)
    sayAudio(text)

def sayAudio(text):
    wav = tts.tts(text, speaker_wav=audio, language="en")
    sd.play(wav, samplerate=23500)
    sd.wait()

def stream_callback(token):
    print(token, end='', flush=True)

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
    response("What would you like to ask AI? Say Take a picture if you would like to take a picture.")
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
                response("What do you want to say?")
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

                response(completion.choices[0].message.content)

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
            response(chat_completion.choices[0].message.content)
    else:
        fullresponse = ""
        response("You are offline, using locally available Llama 3.2. Responses may be delayed")
        for part in generate('llama3', text, stream=True):
            print(part['response'], end='', flush=True)
            fullresponse += part["response"]
        response(fullresponse)
            
def openApp(apps):
    for app in apps:
        try:
            response("Opening " + app)
            open(app, match_closest=True)
        except Exception as e:
            print(e)

def closeApp(apps):
    for app in apps:
        try:
            response("Closing " + app)
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
        response("Are you sure you want to shut down?")        
        text = recognize()
        if "yes" in text:
            os.system('shutdown -s -t 0')
        elif "no" in text:
            response("Shut down cancelled")
    elif action_type == 2:
        response("Are you sure you want to restart?")        
        text = recognize()
        if "yes" in text:
            os.system('shutdown -r -t 0')
        elif "no" in text:
            response("Restart cancelled")

    elif action_type == 3:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def get_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M")
    response("The time is " + str(formatted_time))

def timer():
    response("How many minutes would you like a timer for?")
    minutes = int(re.search(r'\d+', recognize()).group())
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
        response("Voice changed to Andrew")

    else:
        audio = "audio.wav"
        response("Voice changed to Evelyn")


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

def update_label():
    while True:
        global online
        online = is_connected()
        text = recognize(1)
        print(text)
        if text == None:
            continue
        else:
            app.deiconify()
            text=text.lower()
        if "astro" in text:
            print("active")
            if text == "astro":
                print("not")
                text = recognize()
                question_label.configure(text=text)
                print(text)
            else:
                question_label.configure(text=text)

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
def start_background_thread():
    background_thread = threading.Thread(target=update_label, daemon=True)
    background_thread.start()

# Start the background thread before calling app.mainloop()
start_background_thread()
print("running")
app.mainloop()  # Start the Tkinter main loop