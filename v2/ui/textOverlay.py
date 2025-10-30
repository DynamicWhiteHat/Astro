from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QPainter, QFont, QFontMetrics
from PySide6.QtCore import Qt, QRect

class TextOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.text = ""
        self.bg_color = QColor(31, 134, 214, 180) 
        self.font = QFont("Segoe UI", 12)
        self.padding = 10
        self.radius = 10

        if parent:
            self.setFixedWidth(parent.width() // 4)
        self.setFixedHeight(60)

    def setText(self, text):
        self.text = text
        self.resizeToFitText()
        self.update()

    def resizeToFitText(self):
        metrics = QFontMetrics(self.font)
        text_width = self.width() - 2 * self.padding
        rect = metrics.boundingRect(0, 0, text_width, 0, Qt.TextWordWrap, self.text)
        new_height = rect.height() + 2 * self.padding
        self.setFixedHeight(new_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded background
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)

        # Draw text
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(self.font)
        painter.drawText(
            self.rect().adjusted(self.padding, self.padding, -self.padding, -self.padding),
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter,
            self.text
        )
