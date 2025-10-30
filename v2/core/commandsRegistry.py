from core.location import get_location
from commands.weather import get_weather
from core.voice import speaker
from datetime import datetime
from commands.visual import process_screen
from commands.joke import joke
from commands.wikipedia import return_summary
from commands.note import addNote, retrieveToday
from commands.volume import set_volume, volume_up, volume_down, mute, unmute
from commands.ai import askAI
import requests
current_datetime = datetime.now()

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=1.5)
        print(True)
        return True
    except requests.ConnectionError:
        print(False)
        return False
    


# Commands registry for user commands
userCommands = {
    "Weather": lambda ui: get_weather(get_location(), ui) if is_connected() else speaker.yap("Sorry, you need an internet connection to access this feature."),
    "Joke": lambda ui: joke(ui),
    "Screen": lambda ui: process_screen(ui) if is_connected() else speaker.yap("Sorry, you need an internet connection to access this feature."),
    "Time": lambda ui: (ui.showResponseTextSignal.emit(f"The current time is {current_datetime.time().strftime('%I:%M %p')}"), speaker.yap(f"The current time is {current_datetime.time().strftime('%I %M')}")),
    "Date": lambda ui: (ui.showResponseTextSignal.emit(f"Today's date is {current_datetime.strftime('%B %d, %Y')}"),
                    speaker.yap(f"Today's date is {current_datetime.strftime('%B %d, %Y')}")),
    "Wikipedia": lambda command, ui: return_summary(command, ui) if is_connected() else speaker.yap("Sorry, you need an internet connection to access this feature."),
    "Volume Up": lambda: volume_up(),
    "Volume Down": lambda: volume_down(),
    "Set Volume": lambda command: set_volume(command),
    "Mute": lambda: mute(),
    "Unmute": lambda: unmute(),
    "AI": lambda command, ui: askAI(command, ui) if is_connected() else speaker.yap("Sorry, you need an internet connection to access this feature."),
    "Note": lambda command: addNote(command),
    "ReadNote": lambda: retrieveToday(),
    }
