from groq import Groq
from API_KEY import API_KEY
from core.voice import speaker


client = Groq(api_key=API_KEY)


def askAI(query, ui):
    try:
        print("Processing your request, please wait...")
        speaker.yap("Processing your request, please wait...")
        question = query.strip("ask ai")
        if not question:
            speaker.yap("I didn't catch that. Please try again.")
            return
    
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": question + "In your response, remove any special characters like **, \, or other markdown syntax. This will be spoken by a TTS, so any special symbols are not allowed. For math, write out the words, like instead of using the power of two symbol (^2), say 'squared'."
                }
            ]
        )
        
        response = completion.choices[0].message.content.strip()
        print(response)
        ui.showResponseTextSignal.emit(response)
        speaker.yap(response)
    except Exception as e:
        ui.showResponseTextSignal.emit(f"An error occurred while processing your request: {str(e)}")
        speaker.yap(f"An error occurred while processing your request: {str(e)}")