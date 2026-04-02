"""
Professional JARVIS-Style GUI for Bloom AI
Dark theme with cyan/blue accents, animated visualizations, and modern design
"""

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect, QMenuBar, QMenu, QAction, QSystemTrayIcon,
    QStyle, QFileDialog, QMessageBox, QLineEdit
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QRect, QSize, QPoint,
    QParallelAnimationGroup, QEasingCurve, pyqtSignal, QThread,
    QMutex, QMutexLocker
)
from PyQt5.QtGui import (
    QIcon, QFont, QColor, QPalette, QPainter, QPen, QBrush,
    QLinearGradient, QRadialGradient, QConicalGradient,
    QPixmap, QImage, QTextCursor, QTextCharFormat, QTextBlockFormat,
    QKeySequence, QCursor
)
from dotenv import dotenv_values
import sys
import os
import datetime
import wave
import math
import random

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Bloom")
Username = env_vars.get("Username", "User")

# Paths
current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# Ensure directories exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whose', 'whom', 'can you', "what's", "where's", "how's"]
    if any(word + " " in new_query for word in question_words):
        new_query = new_query[:-1] + "?" if query_words[-1][-1] in ['?', '.', '!'] else new_query + "?"
    else:
        new_query = new_query[:-1] + "." if query_words[-1][-1] in ['?', '.', '!'] else new_query + "."
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding="utf-8") as f:
        f.write(Command)

def GetMicrophoneStatus():
    try:
        with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "False"

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as f:
        f.write(Status)

def GetAssistantStatus():
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Ready"

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    with open(TempDirectoryPath('Responses.data'), "w", encoding="utf-8") as f:
        f.write(Text)


# ═══════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════

class CircularProgressRing(QWidget):
    """Animated circular progress ring for loading states."""
    def __init__(self, parent=None, radius=80, pen_width=4, color="#00D4FF"):
        super().__init__(parent)
        self.radius = radius
        self.pen_width = pen_width
        self.color = QColor(color)
        self.progress = 0
        self.angle = 0
        self.setFixedSize(radius * 2 + 20, radius * 2 + 20)
        
    def setProgress(self, value):
        self.progress = max(0, min(100, value))
        self.update()
        
    def startAnimation(self):
        self.anim = QPropertyAnimation(self, b"angle")
        self.anim.setDuration(2000)
        self.anim.setStartValue(0)
        self.anim.setEndValue(360)
        self.anim.setLoopCount(-1)
        self.anim.start()
        
    def getAngle(self):
        return self.angle
        
    def setAngle(self, value):
        self.angle = value
        self.update()
        
    angle = pyqtSignal(int)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background ring
        painter.setPen(QPen(QColor(30, 30, 40), self.pen_width))
        painter.drawArc(
            self.rect().adjusted(10, 10, -10, -10),
            0, 360 * 16
        )
        
        # Progress arc
        painter.setPen(QPen(self.color, self.pen_width))
        span = int((self.progress / 100) * 360 * 16)
        painter.drawArc(
            self.rect().adjusted(10, 10, -10, -10),
            int(self.angle * 16) - 90 * 16, span
        )


class VoiceWaveWidget(QWidget):
    """Animated voice wave visualization."""
    def __init__(self, parent=None, bar_count=40):
        super().__init__(parent)
        self.bar_count = bar_count
        self.heights = [0] * bar_count
        self.target_heights = [0] * bar_count
        self.is_listening = False
        self.setFixedHeight(60)
        
        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateBars)
        self.timer.start(50)
        
    def setListening(self, listening):
        self.is_listening = listening
        if listening:
            self.target_heights = [random.randint(20, 60) for _ in range(self.bar_count)]
        else:
            self.target_heights = [0] * self.bar_count
            
    def updateBars(self):
        for i in range(self.bar_count):
            if self.is_listening:
                self.target_heights[i] = random.randint(15, 55)
            else:
                self.target_heights[i] = max(0, self.target_heights[i] - 5)
            
            # Smooth transition
            diff = self.target_heights[i] - self.heights[i]
            self.heights[i] += diff * 0.3
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        bar_width = width / self.bar_count
        center_y = self.height() / 2
        
        for i, height in enumerate(self.heights):
            x = i * bar_width + bar_width / 2
            h = max(3, height)
            
            # Gradient for each bar
            gradient = QLinearGradient(x, center_y - h/2, x, center_y + h/2)
            gradient.setColorAt(0, QColor("#00D4FF"))
            gradient.setColorAt(0.5, QColor("#00A8CC"))
            gradient.setColorAt(1, QColor("#006B8F"))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            
            rect = QRect(
                int(x - bar_width/3),
                int(center_y - h/2),
                int(bar_width * 0.66),
                int(h)
            )
            painter.drawRoundedRect(rect, 3, 3)


class PulsingOrb(QWidget):
    """Animated pulsing orb for visual effects."""
    def __init__(self, parent=None, size=100, color="#00D4FF"):
        super().__init__(parent)
        self.size = size
        self.base_color = QColor(color)
        self.pulse_scale = 1.0
        self.glow_opacity = 0.3
        self.setFixedSize(size * 2, size * 2)
        
        # Animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pulse)
        self.timer.start(30)
        
    def pulse(self):
        import math
        self.pulse_scale = 1.0 + 0.1 * math.sin(datetime.datetime.now().timestamp() * 3)
        self.glow_opacity = 0.2 + 0.15 * math.sin(datetime.datetime.now().timestamp() * 2)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        radius = self.size * self.pulse_scale
        
        # Outer glow
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0, self.base_color)
        glow.setColorAt(0.5, QColor(self.base_color.red(), self.base_color.green(), self.base_color.blue(), int(100 * self.glow_opacity)))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, int(radius), int(radius))
        
        # Inner core
        core = QRadialGradient(center, radius * 0.3)
        core.setColorAt(0, QColor(255, 255, 255, 200))
        core.setColorAt(0.5, self.base_color)
        core.setColorAt(1, QColor(int(self.base_color.red() * 0.7), int(self.base_color.green() * 0.7), int(self.base_color.blue() * 0.7)))
        
        painter.setBrush(QBrush(core))
        painter.drawEllipse(center, int(radius * 0.4), int(radius * 0.4))


class GlowingButton(QPushButton):
    """Button with glow effect on hover."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00D4FF, stop:1 #0088AA);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00E8FF, stop:1 #00A0CC);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0088AA, stop:1 #006688);
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 212, 255, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


# ═══════════════════════════════════════════════════════════════════
# CHAT WIDGETS
# ═══════════════════════════════════════════════════════════════════

class ChatBubble(QWidget):
    """Chat message bubble with styling."""
    def __init__(self, message="", is_user=False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Sender label
        sender = Username if self.is_user else Assistantname
        sender_label = QLabel(sender)
        sender_label.setStyleSheet(f"""
            color: {'#00D4FF' if not self.is_user else '#FF9500'};
            font-size: 12px;
            font-weight: bold;
        """)
        
        # Message label
        msg_label = QLabel(self.message)
        msg_label.setWordWrap(True)
        msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            line-height: 1.5;
            background: transparent;
        """)
        
        # Time label
        time_label = QLabel(datetime.datetime.now().strftime("%H:%M"))
        time_label.setStyleSheet("""
            color: #666;
            font-size: 10px;
        """)
        time_label.setAlignment(Qt.AlignRight)
        
        if self.is_user:
            layout.addWidget(sender_label, 0, Qt.AlignRight)
            layout.addWidget(msg_label, 0, Qt.AlignRight)
        else:
            layout.addWidget(sender_label, 0, Qt.AlignLeft)
            layout.addWidget(msg_label, 0, Qt.AlignLeft)
        layout.addWidget(time_label)
        
        # Set bubble background
        bubble_color = "#1a3a4a" if not self.is_user else "#2a2a3a"
        border_color = "#00D4FF" if not self.is_user else "#FF9500"
        
        self.setStyleSheet(f"""
            QWidget {{
                background: {bubble_color};
                border-left: 3px solid {border_color};
                border-radius: 10px;
                margin: 5px;
            }}
        """)


# ═══════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════

class JarvisMainWindow(QMainWindow):
    """Main JARVIS-style interface window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize variables
        self.is_maximized = False
        self.mic_enabled = False
        
        # Setup UI
        self.initUI()
        
        # Setup timers
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(100)
        
        self.response_timer = QTimer(self)
        self.response_timer.timeout.connect(self.checkForResponses)
        self.response_timer.start(200)
        
        # Set initial status
        SetMicrophoneStatus("False")
        SetAssistantStatus("Ready")
        
    def initUI(self):
        """Initialize the user interface."""
        # Main container
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a12, stop:0.5 #0d0d1a, stop:1 #080810);
                border-radius: 15px;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        self.main_widget.setGraphicsEffect(shadow)
        
        self.setCentralWidget(self.main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        main_layout.addWidget(self.createTitleBar())
        
        # Central content
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(20, 10, 20, 20)
        
        # Top section - Orb and status
        top_section = self.createTopSection()
        central_layout.addWidget(top_section)
        
        # Chat area
        chat_area = self.createChatArea()
        central_layout.addWidget(chat_area, 1)
        
        # Voice visualization
        voice_section = self.createVoiceSection()
        central_layout.addWidget(voice_section)
        
        # Bottom controls
        bottom_controls = self.createBottomControls()
        central_layout.addWidget(bottom_controls)
        
        main_layout.addWidget(central)
        
        # Window geometry
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(100, 100, min(1200, screen.width() - 200), min(800, screen.height() - 100))
        
    def createTitleBar(self):
        """Create custom title bar."""
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0a0a12, stop:1 #12121f);
                border-bottom: 1px solid #1a1a2e;
            }
        """)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 5, 0)
        
        # Title
        title = QLabel(f"⚡ {Assistantname} AI")
        title.setStyleSheet("""
            color: #00D4FF;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        
        # Window controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setSpacing(0)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_style = """
            QPushButton {
                background: transparent;
                color: #888;
                border: none;
                width: 40px;
                height: 30px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #333;
                color: white;
            }
        """
        
        self.min_btn = QPushButton("─")
        self.min_btn.setStyleSheet(btn_style)
        self.min_btn.clicked.connect(self.showMinimized)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setStyleSheet(btn_style)
        self.max_btn.clicked.connect(self.toggleMaximize)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setStyleSheet(btn_style.replace("color: #888;", "color: #888;").replace("background: #333;", "background: #c42b1c;"))
        self.close_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(self.min_btn)
        controls_layout.addWidget(self.max_btn)
        controls_layout.addWidget(self.close_btn)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(controls)
        
        # Make title bar draggable
        self.title_bar = title_bar
        self.draggable = True
        self.drag_offset = QPoint()
        
        def mousePress(event):
            if event.button() == Qt.LeftButton:
                self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
                
        def mouseMove(event):
            if event.buttons() == Qt.LeftButton and self.draggable:
                self.move(event.globalPos() - self.drag_offset)
                
        title_bar.mousePressEvent = mousePress
        title_bar.mouseMoveEvent = mouseMove
        
        return title_bar
        
    def createTopSection(self):
        """Create top section with orb and status."""
        section = QWidget()
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 20, 0, 20)
        
        # Left side - Orb
        orb_container = QWidget()
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setAlignment(Qt.AlignCenter)
        
        self.orb = PulsingOrb(size=60, color="#00D4FF")
        orb_layout.addWidget(self.orb)
        
        # Status text
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            color: #00D4FF;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        orb_layout.addWidget(self.status_label)
        
        layout.addWidget(orb_container, 1)
        
        # Right side - Info
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            color: #00D4FF;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        self.updateTime()
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            color: #666;
            font-size: 12px;
            font-family: 'Segoe UI', Arial;
        """)
        self.updateDate()
        
        info_layout.addWidget(self.time_label)
        info_layout.addWidget(self.date_label)
        
        # Timer for clock
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self.updateTime)
        clock_timer.timeout.connect(self.updateDate)
        clock_timer.start(1000)
        
        layout.addWidget(info_container, 1)
        
        return section
        
    def createChatArea(self):
        """Create chat message area."""
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setFrameShape(QScrollArea.NoFrame)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: 1px solid #1a1a2e;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #00D4FF;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        
        self.chat_scroll.setWidget(self.chat_container)
        
        return self.chat_scroll
        
    def createVoiceSection(self):
        """Create voice wave visualization section."""
        section = QWidget()
        section.setFixedHeight(80)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 10, 0, 10)
        
        # Voice wave
        self.voice_wave = VoiceWaveWidget(bar_count=50)
        self.voice_wave.setStyleSheet("background: transparent;")
        layout.addWidget(self.voice_wave)
        
        # Listening status
        self.listening_label = QLabel("🎤 Click to speak")
        self.listening_label.setAlignment(Qt.AlignCenter)
        self.listening_label.setStyleSheet("""
            color: #888;
            font-size: 12px;
        """)
        layout.addWidget(self.listening_label)
        
        return section
        
    def createBottomControls(self):
        """Create bottom control bar."""
        controls = QWidget()
        controls.setFixedHeight(80)
        controls.setStyleSheet("""
            QWidget {
                background: #0a0a12;
                border-top: 1px solid #1a1a2e;
                border-radius: 0px 0px 15px 15px;
            }
        """)
        
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(20, 5, 20, 15)
        
        # Microphone button
        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(50, 50)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a3a4a, stop:1 #0d1f2a);
                border: 2px solid #00D4FF;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a5a6a, stop:1 #1d3f4a);
            }
            QPushButton:pressed {
                background: #00D4FF;
            }
        """)
        self.mic_btn.clicked.connect(self.toggleMic)
        
        # Text input field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your command here...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: #1a1a2e;
                border: 1px solid #333;
                border-radius: 15px;
                padding: 8px 15px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00D4FF;
            }
            QLineEdit::placeholder {
                color: #555;
            }
        """)
        self.text_input.returnPressed.connect(self.sendTextInput)
        
        # Send button
        send_btn = QPushButton("➤")
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00D4FF, stop:1 #0088AA);
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00E8FF, stop:1 #00A0CC);
            }
        """)
        send_btn.clicked.connect(self.sendTextInput)
        
        # Settings button
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #333;
                border-radius: 20px;
                color: #888;
                font-size: 18px;
            }
            QPushButton:hover {
                border-color: #00D4FF;
                color: #00D4FF;
            }
        """)
        settings_btn.clicked.connect(self.showSettings)
        
        layout.addWidget(self.mic_btn)
        layout.addWidget(self.text_input, 1)
        layout.addWidget(send_btn)
        layout.addWidget(settings_btn)
        
        return controls
    
    def sendTextInput(self):
        """Send text input to the assistant."""
        text = self.text_input.text().strip()
        if text:
            # Write to temp file for Main.py to read
            try:
                with open(TempDirectoryPath('TextInput.data'), 'w', encoding='utf-8') as f:
                    f.write(text)
                self.text_input.clear()
            except Exception as e:
                print(f"Error sending text: {e}")
        
    def toggleMic(self):
        """Toggle microphone on/off."""
        self.mic_enabled = not self.mic_enabled
        self.voice_wave.setListening(self.mic_enabled)
        
        if self.mic_enabled:
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: #00D4FF;
                    border: 2px solid #00D4FF;
                    border-radius: 25px;
                    font-size: 20px;
                }
            """)
            SetMicrophoneStatus("True")
            self.listening_label.setText("🎤 Listening...")
            self.listening_label.setStyleSheet("color: #00D4FF; font-size: 12px;")
            self.status_label.setText("Listening...")
        else:
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1a3a4a, stop:1 #0d1f2a);
                    border: 2px solid #00D4FF;
                    border-radius: 25px;
                    font-size: 20px;
                }
            """)
            SetMicrophoneStatus("False")
            self.listening_label.setText("🎤 Click to speak")
            self.listening_label.setStyleSheet("color: #888; font-size: 12px;")
            self.status_label.setText("Ready")
            
    def toggleMaximize(self):
        """Toggle window maximize/restore."""
        if self.is_maximized:
            self.showNormal()
            self.max_btn.setText("□")
        else:
            self.showMaximized()
            self.max_btn.setText("❐")
        self.is_maximized = not self.is_maximized
        
    def updateTime(self):
        """Update the time display."""
        self.time_label.setText(datetime.datetime.now().strftime("%H:%M"))
        
    def updateDate(self):
        """Update the date display."""
        self.date_label.setText(datetime.datetime.now().strftime("%d %B %Y"))
        
    def updateStatus(self):
        """Update assistant status."""
        status = GetAssistantStatus()
        self.status_label.setText(status)
        
        if "Listening" in status:
            self.status_label.setStyleSheet("color: #00D4FF; font-size: 14px; font-weight: bold;")
        elif "Thinking" in status or "Processing" in status:
            self.status_label.setStyleSheet("color: #FF9500; font-size: 14px; font-weight: bold;")
        elif "Speaking" in status or "Answering" in status:
            self.status_label.setStyleSheet("color: #00FF88; font-size: 14px; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #00D4FF; font-size: 14px; font-weight: bold;")
            
    def checkForResponses(self):
        """Check for new responses to display."""
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding="utf-8") as f:
                response = f.read().strip()
                
            if response and hasattr(self, 'last_response') and response != self.last_response:
                self.addMessage(response, is_user=False)
            self.last_response = response
        except:
            pass
            
    def addMessage(self, message, is_user=True):
        """Add a message to the chat."""
        bubble = ChatBubble(message, is_user)
        self.chat_layout.addWidget(bubble)
        
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
        
    def showSettings(self):
        """Show settings menu."""
        msg = QMessageBox(self)
        msg.setWindowTitle(f"{Assistantname} Settings")
        msg.setText(f"""
            <h3>⚡ {Assistantname} AI</h3>
            <p>Version 1.0</p>
            <p>Your personal AI assistant</p>
            <hr>
            <p><b>Commands you can try:</b></p>
            <ul>
                <li>"Open Notepad"</li>
                <li>"Search for Python tutorials"</li>
                <li>"Create a folder on Desktop"</li>
                <li>"Play music on YouTube"</li>
                <li>"Generate image of a sunset"</li>
                <li>"What's the weather?"</li>
            </ul>
        """)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def GraphicalUserInterface():
    """Launch the JARVIS-style GUI."""
    print("GUI: Creating application...")
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("GUI: Setting style...")
    app.setStyle('Fusion')
    
    # Set application-wide stylesheet
    app.setStyleSheet("""
        QToolTip {
            background: #1a1a2e;
            color: #00D4FF;
            border: 1px solid #00D4FF;
            padding: 5px;
            border-radius: 5px;
        }
    """)
    
    print("GUI: Creating window...")
    window = JarvisMainWindow()
    
    print("GUI: Showing window...")
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("GUI: Starting event loop...")
    sys.stdout.flush()
    
    result = app.exec_()
    print(f"GUI: Event loop ended with code {result}")
    return result


if __name__ == "__main__":
    sys.exit(GraphicalUserInterface())
