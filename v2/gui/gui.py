import sys
import math
from PySide6.QtCore import Qt, QRect, Signal, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QColor, QPainter
from gui.textOverlay import TextOverlay

class AssistantWindow(QMainWindow):
    # Signals
    setTextSignal = Signal(str)
    showSignal = Signal()
    hideSignal = Signal()
    stopSignal = Signal()
    startPulseSignal = Signal()
    stopPulseSignal = Signal()
    showUserTextSignal = Signal(str)
    showResponseTextSignal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Assistant Overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()

        # Pulse bar
        self.base_color = QColor(31, 134, 214, 180)
        self.pulse_phase = 0.0
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.updatePulse)
        self.pulsing = False

        # Connections
        self.showSignal.connect(self.fadeIn)
        self.hideSignal.connect(self.fadeOut)
        self.startPulseSignal.connect(self.startPulse)
        self.stopPulseSignal.connect(self.stopPulse)

        self._fade_anim = None

        # Screen info
        screen_width = self.width()
        screen_height = self.height()
        overlay_width = screen_width // 4
        overlay_height = 60
        self.margin = 10
        self.bottom_margin = 100

        # Create text overlays
        self.responseOverlay = TextOverlay(self)
        self.responseOverlay.setGeometry(
            self.margin,
            screen_height - self.bottom_margin - overlay_height,
            overlay_width,
            overlay_height
        )

        self.userOverlay = TextOverlay(self)
        self.userOverlay.setGeometry(
            self.margin,
            screen_height - self.bottom_margin - overlay_height - overlay_height - self.margin,
            overlay_width,
            overlay_height
        )

        self.userOverlay.hide()
        self.responseOverlay.hide()

        # Signals to show text
        self.showUserTextSignal.connect(lambda text: self.showUserText(text))
        self.showResponseTextSignal.connect(lambda text: self.showResponseText(text))

    # --- Pulse bar ---
    def startPulse(self):
        if not self.pulsing:
            self.pulsing = True
            self.pulse_phase = 0.0
            self.pulse_timer.start(16)

    def stopPulse(self):
        if self.pulsing:
            self.pulsing = False
            self.pulse_timer.stop()
            self.update()

    def updatePulse(self):
        self.pulse_phase += 0.05
        self.update()

    # --- Fade animations ---
    def fadeIn(self):
        self.setWindowOpacity(0)
        self.show()
        self.startPulse()

        self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(400)
        self._fade_anim.setStartValue(0)
        self._fade_anim.setEndValue(1)
        self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_anim.start()

    def fadeOut(self):
        self.stopPulse()
        self.userOverlay.hide()
        self.responseOverlay.hide()

        self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(400)
        self._fade_anim.setStartValue(self.windowOpacity())
        self._fade_anim.setEndValue(0)
        self._fade_anim.setEasingCurve(QEasingCurve.InCubic)
        self._fade_anim.finished.connect(self.hide)
        self._fade_anim.start()

    # --- Mouse interaction ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.hideSignal.emit()
            self.stopSignal.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))  # dim background

        bar_height = 20
        top = self.height() - bar_height

        if self.pulsing:
            pulse = (math.sin(self.pulse_phase) + 1) / 2
            r = int(self.base_color.red() + pulse * (255 - self.base_color.red()))
            g = int(self.base_color.green() + pulse * (255 - self.base_color.green()))
            b = int(self.base_color.blue() + pulse * (255 - self.base_color.blue()))
            alpha = 180
            color = QColor(r, g, b, alpha)
        else:
            color = self.base_color

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRect(0, top, self.width(), bar_height))

    # --- Show text overlays ---
    def showUserText(self, text: str):
        self.userOverlay.setText(text)
        self.userOverlay.show()
        self.adjustOverlays()

    def showResponseText(self, text: str):
        self.responseOverlay.setText(text)
        self.responseOverlay.show()
        self.adjustOverlays()

    # --- Adjust positions ---
    def adjustOverlays(self):
        screen_height = self.height()

        resp_height = self.responseOverlay.height()
        self.responseOverlay.move(
            self.responseOverlay.x(),
            screen_height - self.bottom_margin - resp_height
        )

        user_height = self.userOverlay.height()
        margin = self.margin
        self.userOverlay.move(
            self.userOverlay.x(),
            screen_height - self.bottom_margin - resp_height - margin - user_height
        )
