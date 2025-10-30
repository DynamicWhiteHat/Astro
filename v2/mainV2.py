import sys
import threading
import time
from PySide6.QtWidgets import QApplication
from threading import Event

from gui.gui import AssistantWindow
from RealtimeSTT import AudioToTextRecorder
from core.sentenceClassifier import processCommand
from commands.note import createTable

stop_event = Event()

def run_voice_assistant(ui):
    createTable()

    recorder = AudioToTextRecorder(
        wakeword_backend="oww",
        wake_words_sensitivity=0.35,
        openwakeword_model_paths="v2/models/astro.onnx,",
        wake_words="astro",
        wake_word_timeout=3,
        on_recording_start=ui.showSignal.emit
    )

    while True:
        if stop_event.is_set():
            stop_event.clear()
            continue
        command = recorder.text()
        ui.showUserTextSignal.emit(command)
        ui.stopPulseSignal.emit()
        processCommand(command, ui)
        ui.hideSignal.emit()

        # Check for stop event between commands
        if stop_event.is_set():
            stop_event.clear()


if __name__ == "__main__":
    if QApplication.instance() is not None:
        QApplication.instance().quit()
    app = QApplication(sys.argv)
    ui = AssistantWindow()
    ui.hide()

    ui.stopSignal.connect(lambda: stop_event.set())

    assistant_thread = threading.Thread(target=run_voice_assistant, args=(ui,), daemon=True)
    assistant_thread.start()

    sys.exit(app.exec())
