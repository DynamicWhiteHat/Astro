import tkinter as tk
from tkinter import font

def adjust_question_frame_size(event=None):
    # Adjust the height of the question frame based on the content
    question_canvas.update_idletasks()
    content_height = question_label.winfo_height()
    max_height = 55  # Maximum height for the question frame
    new_height = min(content_height, max_height)  # Don't exceed max height
    question_canvas.config(height=new_height)

def adjust_response_frame_size(event=None):
    # Adjust the height of the response frame based on the content
    response_canvas.update_idletasks()
    content_height = response_label.winfo_height()
    max_height = 150  # Maximum height for the response frame
    min_height = 55   # Minimum height for the response frame
    new_height = min(max(content_height, min_height), max_height)  # Adjust between min and max height
    response_canvas.config(height=new_height)

    # Adjust the main frame height dynamically
    total_height = 55 + question_canvas.winfo_height() + new_height
    app.geometry(f"500x{total_height}")  # Adjust the window height dynamically

# App setup
app = tk.Tk()
Montserrat = font.Font(family="Montserrat", size=12, weight="bold")
Montserrat_line = font.Font(family="Montserrat", size=12, weight="bold", underline=True)

app.geometry("+1290+10")
app.maxsize(width=500, height=200)
app.overrideredirect(True)

frame = tk.Frame(app, width=500, height=150)
frame.pack(fill="both", expand=True)

# Scrollable frame for the Question section
question_canvas = tk.Canvas(frame, width=480, height=55, highlightthickness=0)
question_canvas.place(x=10, y=10)
question_frame = tk.Frame(question_canvas, bg="")
question_scroll = tk.Scrollbar(frame, orient="vertical", command=question_canvas.yview)
question_scroll.place(x=490, y=10, height=55)
question_canvas.create_window((0, 0), window=question_frame, anchor="nw")
question_canvas.configure(yscrollcommand=question_scroll.set)

question_label = tk.Label(question_frame, text="Testing", font=Montserrat_line, fg="#FFFFFF", bg="#000000")
question_label.pack(pady=5, padx=5, anchor="nw")

# Scrollable frame for the Response section
response_canvas = tk.Canvas(frame, width=480, height=55, highlightthickness=0)
response_canvas.place(x=10, y=75)
response_frame = tk.Frame(response_canvas, bg="")
response_scroll = tk.Scrollbar(frame, orient="vertical", command=response_canvas.yview)
response_scroll.place(x=490, y=75, height=55)
response_canvas.create_window((0, 0), window=response_frame, anchor="nw")
response_canvas.configure(yscrollcommand=response_scroll.set)

response_label = tk.Label(response_frame, text="Response\n" * 5, font=Montserrat, fg="#FFFFFF", bg="#000000")
response_label.pack(pady=5, padx=5, anchor="nw")

# Adjust the question and response frame size dynamically
question_label.bind("<Configure>", adjust_question_frame_size)
response_label.bind("<Configure>", adjust_response_frame_size)

app.mainloop()
