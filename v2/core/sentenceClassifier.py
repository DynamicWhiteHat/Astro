import joblib
import inspect
from core.commandsRegistry import userCommands
from core.voice import speaker
import os
import keyboard
import threading


# Load the model
model = joblib.load('models/intent_classifier.joblib')

def wait_for_cancel():
    # Wait for Escape key
    keyboard.wait('esc')
    os.system("shutdown /a")
    speaker.yap("Operation canceled")
    print("Operation canceled.")

def processCommand(command, ui,):
    command = command.lower()
    print(command)
    if command.strip(".") in ["shut down", "shutdown"]:
        speaker.yap("Shutting down in 5 seconds. Press Escape to cancel.")
        print("Shutting down... Press Escape to cancel.")
        ui.hideSignal.emit()
        threading.Thread(target=wait_for_cancel, daemon=True).start()
        os.system("shutdown /s /t 5")
        return

    elif command.strip(".") in ["restart", "reboot"]:
        speaker.yap("Restarting in 5 seconds. Press Escape to cancel.")
        print("Restarting... Press Escape to cancel.")
        ui.hideSignal.emit()
        threading.Thread(target=wait_for_cancel, daemon=True).start()
        os.system("shutdown /r /t 5")
        return

    elif command.strip(".") in ["log off", "sign out"]:
        speaker.yap("Logging off in 5 seconds.")
        print("Logging off...")
        ui.hideSignal.emit()
        os.system("shutdown /l")
        return
    elif (command.strip(".")  == "sleep" or command.strip(".")  == "hibernate"):
        print("Sleeping...")
        ui.hideSignal.emit()

        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return
    elif command.strip(".") in ["power down", "terminate", "end session"]:
        speaker.yap("Goodbye")
        ui.hideSignal.emit()
        os._exit(0)
        return
    # Predict intent
    intent = model.predict([command])[0]
    print(f"Detected intent: {intent}")
    
    action = userCommands[intent]
    
    sig = inspect.signature(action)
    params = list(sig.parameters.keys())
    
    kwargs = {}
    if "command" in params:
        kwargs["command"] = command
    if "ui" in params:
        kwargs["ui"] = ui
    
    action(**kwargs)
    
    print("Done")
