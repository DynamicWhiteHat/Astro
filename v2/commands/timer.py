import re
import time
import threading
from core.voice import speaker
from pygame import mixer

mixer.init()


# Mapping of text numbers to integers
TEXT_NUMBERS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
}

def text_to_int(text):
    text = text.lower().replace("-", " ")
    parts = text.split()
    total = 0
    for part in parts:
        if part in TEXT_NUMBERS:
            total += TEXT_NUMBERS[part]
    return total

def parse_time(text):
    text = text.lower()
    
    hours = re.search(r'(\d+|\w+)\s*hour', text)
    minutes = re.search(r'(\d+|\w+)\s*minute', text)
    seconds = re.search(r'(\d+|\w+)\s*second', text)
    
    # Convert matches to int
    def convert(match):
        if match is None:
            return 0
        value = match.group(1)
        if value.isdigit():
            return int(value)
        return text_to_int(value)
    
    return convert(hours), convert(minutes), convert(seconds)

def total_seconds(hours, minutes, seconds):
    return hours * 3600 + minutes * 60 + seconds

def timer_thread(duration):
    time.sleep(duration)
    mixer.music.play()
    print("Time's up!")
    speaker.yap("Your timer is up!")


def format_timer_message(hours, minutes, seconds):
    parts = []
    
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    if len(parts) == 0:
        return "0 seconds"
    elif len(parts) == 1:
        return parts[0]
    else:
        return ', '.join(parts[:-1]) + ' and ' + parts[-1]

def start_timer(text):
    mixer.music.load('sounds/timer.mp3')
    hours, minutes, seconds = parse_time(text)
    duration = total_seconds(hours, minutes, seconds)
    message = format_timer_message(hours, minutes, seconds)
    print(f"Starting timer for {message}.")
    speaker.yap(f"Starting timer for {message}.")
    
    thread = threading.Thread(target=timer_thread, args=(duration,))
    thread.daemon = True
    thread.start()
    
    return thread
