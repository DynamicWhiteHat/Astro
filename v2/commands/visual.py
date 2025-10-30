from mss import mss
from core.voice import speaker
from API_KEY import API_KEY
from PIL import Image
from groq import Groq
import base64
import io

def process_screen(ui):
    try:
        # Capture the screen and convert to Base64
        base64_image = capture_screen_base64()
        sendAI(base64_image, ui)
    except Exception as e:
        ui.showResponseTextSignal.emit("An error occurred while processing the screen.")
        speaker.yap(f"An error occurred while processing the screen: {str(e)}")

def capture_screen_base64():
    with mss() as sct:
        screenshot = sct.grab(sct.monitors[0])

        # Convert to PIL image
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return img_base64

def sendAI(base64_image, ui):

    client = Groq(api_key=API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Can you describe this image? What do you see? Keep it short, about 1 sentence."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    non_speakable_chars = [
    '*', '_', '~', '`', '^', '#', '@', '|', '\\', '/', '=', '+', '<', '>', 
    '[', ']', '{', '}', '(', ')', '%', '$', '&', '"', "'", ';', ':'
    ]
    for char in non_speakable_chars:
        chat_completion.choices[0].message.content = chat_completion.choices[0].message.content.replace(char, "")

    print(chat_completion.choices[0].message.content.strip("*"))
    ui.showResponseTextSignal.emit(chat_completion.choices[0].message.content)
    speaker.yap(chat_completion.choices[0].message.content)