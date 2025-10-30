import joblib
import inspect
from core.commandsRegistry import userCommands
# Load the model
model = joblib.load('v2/models/intent_classifier.joblib')

def processCommand(command, ui):
    print(command)
    
    # Predict intent
    intent = model.predict([command])[0]
    print(f"Detected intent: {intent}")
    
    # Get the action function for the intent
    action = userCommands[intent]
    
    # Inspect function parameters
    sig = inspect.signature(action)
    params = list(sig.parameters.keys())
    
    # Prepare kwargs based on function parameters
    kwargs = {}
    if "command" in params:
        kwargs["command"] = command
    if "ui" in params:
        kwargs["ui"] = ui
    
    # Call the action with kwargs
    action(**kwargs)
    
    print("Done")
