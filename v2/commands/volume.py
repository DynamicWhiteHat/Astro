import pyautogui
import re

def volume_up():
    pyautogui.press('volumeup', 2)
    
def volume_down():
    pyautogui.press('volumedown', 2)

def mute():
    pyautogui.press('volumemute')

def unmute():
    pyautogui.press('volumeup', 2)
    pyautogui.press('volumedown', 2)

def set_volume(command):
    pyautogui.press('volumedown', 50)
    match = re.findall(r'\d+', command)
    if match:
        setpoint = int(match[0]) 
        print(setpoint)
        pyautogui.press('volumeup', round(setpoint / 2))
    else:
        print("No valid number found in the command.")