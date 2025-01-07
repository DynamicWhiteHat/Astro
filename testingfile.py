from customtkinter import *

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
app.overrideredirect(True)

frame = CTkFrame(master=app, width=500, height=150)
frame.pack(fill="both", expand=True)

# Scrollable frame for the Question section
question_frame = CTkScrollableFrame(frame, width=480, height=55, fg_color="transparent")
question_frame.place(x=10, y=10)
question_frame._scrollbar.configure(height=0)
question_label = CTkLabel(master=question_frame, text="Testing", font=Montserrat_line, text_color="#FFFFFF")
question_label.pack(pady=5, padx=5, anchor="nw")

# Scrollable frame for the Response section
response_frame = CTkScrollableFrame(master=frame, width=480, height=55, fg_color="transparent")
response_frame.place(x=10, y=75)  # Top padding of 10px + question_frame height (55) + 10px gap
response_frame._scrollbar.configure(height=0)
response_label = CTkLabel(master=response_frame, text="Response\n" * 1, font=Montserrat, text_color="#FFFFFF")
response_label.pack(pady=5, padx=5, anchor="nw")

# Adjust the question and response frame size dynamically
question_label.bind("<Configure>", adjust_question_frame_size)
response_label.bind("<Configure>", adjust_response_frame_size)

app.mainloop()
