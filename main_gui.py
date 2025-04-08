import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                            QLabel, QFrame, QHBoxLayout, QGraphicsDropShadowEffect,
                            QProgressBar, QSizePolicy, QSpacerItem, QGridLayout)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, QRect, QPoint
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap, QPainter, QPen, QBrush, QPainterPath, QLinearGradient
from upd_deadlock import DeadlockDetectorGUI
import psutil


try:
    import ai_powered_deadlock as pa
    ai_module_available = True
except Exception as e:
    print(f"Warning: Could not import ai_powered_deadlock module: {e}")
    ai_module_available = False

class CircularProgressBar(QWidget):
    def __init__(self, parent=None, value=0, max_value=100, width=150, height=150,
                progress_color=QColor("#4FA1D8"), background_color=QColor("#E0E0E0"),
                text_color=QColor("#333333"), suffix="%"):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value
        self.progress_color = progress_color
        self.background_color = background_color
        self.text_color = text_color
        self.suffix = suffix
        self.setFixedSize(width, height)
        
    def setValue(self, value):
        self.value = value
        self.update()
        
    def setColors(self, progress_color, background_color, text_color):
        self.progress_color = progress_color
        self.background_color = background_color
        self.text_color = text_color
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    
        width = self.width()
        height = self.height()
        pen_width = width * 0.08
        margin = pen_width / 2
        
       
        rect = QRect(int(margin), int(margin), int(width - 2 * margin), int(height - 2 * margin))
        
        
        angle = int(360 * (self.value / self.max_value))
        
       
        painter.setPen(QPen(self.background_color, pen_width, Qt.PenStyle.SolidLine))
        painter.drawArc(rect, 0, 360 * 16)    
        
      
        painter.setPen(QPen(self.progress_color, pen_width, Qt.PenStyle.SolidLine))
        painter.drawArc(rect, 90 * 16, -angle * 16)            
        
        text = f"{int(self.value)}{self.suffix}"
        painter.setPen(self.text_color)
        painter.setFont(QFont("Segoe UI", int(width / 10), QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

class AnimatedToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(60, 30)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
       
        track_color = QColor("#CCCCCC") if not self.isChecked() else QColor("#4FA1D8")
        thumb_color = QColor("white")
        icon_color = QColor("#4FA1D8") if not self.isChecked() else QColor("white")
        
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
         
        thumb_x = 35 if self.isChecked() else 5
        
        
        painter.setBrush(QBrush(thumb_color))
        painter.drawEllipse(thumb_x, 5, 20, 20)
        
        
        painter.setPen(icon_color)
        painter.setFont(QFont("Segoe UI", 10))
        
        if self.isChecked():
            painter.drawText(QRect(thumb_x, 5, 20, 20), Qt.AlignmentFlag.AlignCenter, "🌙")
        else:
            painter.drawText(QRect(thumb_x, 5, 20, 20), Qt.AlignmentFlag.AlignCenter, "☀️")

class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.dark_mode = False   
        self.animation_duration = 300   
        self.system_uptime = 0   
        self.initUI()
        
         
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  
        
    def update_stats(self):
        
        self.system_uptime += 1
        hours, remainder = divmod(self.system_uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        
        if self.system_uptime > 0:
            uptime_text = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.uptime_value.setText(uptime_text)
        
        
        try:
             
            cpu_percent = psutil.cpu_percent(interval=0.1)  
            cpu_percent = round(cpu_percent, 1)
            self.cpu_progress.setValue(cpu_percent)
            
            
            if self.system_uptime % 5 == 0:  
                print(f"Current CPU Usage: {cpu_percent}%")
        except Exception as e:
            print(f"Error getting CPU usage: {e}")
            
            self.cpu_progress.setValue(0)
        
    def initUI(self):
        # Main window setup
        self.setWindowTitle("Deadlock Detection System")
        self.setGeometry(300, 300, 1100, 700)
        
        # Main layout with proper spacing
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header - unified design
        header = QFrame()
        header.setObjectName("header")
        header.setMinimumHeight(70)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(20)
        
        # CPU Load with circular progress (left side)
        cpu_layout = QHBoxLayout()
        cpu_layout.setSpacing(15)
        
        cpu_title = QLabel("CPU Load")
        cpu_title.setFont(QFont("Segoe UI", 11))
        cpu_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.cpu_progress = CircularProgressBar(value=0, width=40, height=40)
        
        cpu_layout.addWidget(cpu_title)
        cpu_layout.addWidget(self.cpu_progress)
        
        # Title in center
        title_label = QLabel("DEADLOCK DETECTION SYSTEM")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Uptime and theme toggle (right side)
        right_layout = QHBoxLayout()
        right_layout.setSpacing(15)
        
        # System uptime
        uptime_layout = QHBoxLayout()
        uptime_layout.setSpacing(10)
        
        uptime_icon = QLabel("⏱️")
        uptime_icon.setFont(QFont("Segoe UI", 12))
        
        self.uptime_value = QLabel("00:00:00")
        self.uptime_value.setFont(QFont("Segoe UI", 11))
        
        uptime_layout.addWidget(uptime_icon)
        uptime_layout.addWidget(self.uptime_value)
        
        # Theme toggle button
        theme_label = QLabel("Theme")
        theme_label.setFont(QFont("Segoe UI", 11))
        
        self.theme_toggle = AnimatedToggleButton()
        self.theme_toggle.setChecked(self.dark_mode)
        self.theme_toggle.toggled.connect(self.toggle_theme)
        
        right_layout.addLayout(uptime_layout)
        right_layout.addWidget(theme_label)
        right_layout.addWidget(self.theme_toggle)
        
        
        header_layout.addLayout(cpu_layout)
        header_layout.addStretch(1)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addLayout(right_layout)
        
        # Add header to main layout
        main_layout.addWidget(header)
        
        # Cards container with grid layout
        cards_container = QFrame()
        cards_layout = QGridLayout(cards_container)
        cards_layout.setSpacing(30)
        cards_layout.setContentsMargins(10, 10, 10, 10)
        
        
        sim_card = self.create_improved_card(
            "Deadlock Simulator",
            "🛠️",
            "Run simulations to analyze potential deadlock scenarios in your system. This tool allows you to create and visualize process resource allocation graphs to understand and prevent deadlocks.",
            "LAUNCH SIMULATOR",
            self.open_simulator
        )
        
        detector_card = self.create_improved_card(
            "Real-time Detection", 
            "⌚",
            "This Module currently fetches current running processes in real-time for one instant and then detects potential deadlocks in current runnning proceses also displays memory vs processes graph",
            "LAUNCH DETECTOR", 
            self.open_detector,
            enabled=ai_module_available
        )
        
        cards_layout.addWidget(sim_card, 0, 0)
        cards_layout.addWidget(detector_card, 0, 1)
        
        main_layout.addWidget(cards_container)
        
        # Status bar with activity indicator - unified design
        footer = QFrame()
        footer.setFixedHeight(40)
        footer.setObjectName("footer")
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 0, 15, 0)
        
        # Pulsing activity indicator
        activity_indicator = QFrame()
        activity_indicator.setFixedSize(12, 12)
        activity_indicator.setObjectName("activityIndicator")
        
        status_label = QLabel("SYSTEM ACTIVE • v2.1")
        status_label.setFont(QFont("Segoe UI", 9))
        status_label.setObjectName("status")
        
        credits_label = QLabel("© 2024 Deadlock Detection Team")
        credits_label.setFont(QFont("Segoe UI", 9))
        credits_label.setObjectName("credits")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        footer_layout.addWidget(activity_indicator)
        footer_layout.addWidget(status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(credits_label)
        
        main_layout.addWidget(footer)
        
        # Set the main layout
        self.setLayout(main_layout)
        
        # Apply the theme after all widgets are created
        self.apply_theme()
    
    def apply_theme(self):
        # Update circular progress colors based on theme
        if hasattr(self, 'cpu_progress'):
            if self.dark_mode:
                self.cpu_progress.setColors(QColor("#4FA1D8"), QColor("#555555"), QColor("#FFFFFF"))
            else:
                self.cpu_progress.setColors(QColor("#4FA1D8"), QColor("#E0E0E0"), QColor("#333333"))
        
        # Apply unified theme to all elements
        if self.dark_mode:
            # Dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #1E1E1E;
                    color: #F0F0F0;
                    font-family: 'Segoe UI', Arial;
                }
                
                /* Header and footer get subtle distinction */
                QFrame#header, QFrame#footer {
                    background-color: #252525;
                    border-radius: 8px;
                    border: 1px solid #333333;
                }
                
                QLabel#title {
                    color: #FFFFFF;
                    font-weight: bold;
                }
                
                /* Standard buttons */
                QPushButton {
                    background-color: #4FA1D8;
                    color: white;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3A7CA5;
                }
                QPushButton:pressed {
                    background-color: #2C5F7F;
                }
                QPushButton:disabled {
                    background-color: #444444;
                    color: #888888;
                }
                
                /* Cards have subtle border instead of different background */
                QFrame.card {
                    border: 1px solid #333333;
                    border-radius: 8px;
                }
                
                QFrame.card QLabel.card-title {
                    color: #4FA1D8;
                    font-weight: bold;
                    ackground-color: transparent;
                }
                
                QFrame.card QLabel.card-description {
                    color: #BBBBBB;
                    background-color: transparent;
                }
                
                QFrame#activityIndicator {
                    background-color: #4FA1D8;
                    border-radius: 6px;
                }
                
                QLabel#status, QLabel#credits {
                    color: #AAAAAA;
                }
                QFrame#header QLabel, QFrame#header QWidget {
                    background-color: transparent;
                }
                QFrame.card QLabel, QFrame.card QHBoxLayout, QFrame.card QVBoxLayout {
                    background-color: transparent;
                }

            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #F5F5F5;
                    color: #333333;
                    font-family: 'Segoe UI', Arial;
                }
                
                /* Header and footer get subtle distinction */
                QFrame#header, QFrame#footer {
                    background-color: #FFFFFF;
                    border-radius: 8px;
                    border: 1px solid #E0E0E0;
                }
                
                QLabel#title {
                    color: #333333;
                    font-weight: bold;
                }
                
                /* Standard buttons */
                QPushButton {
                    background-color: #4FA1D8;
                    color: white;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3A7CA5;
                }
                QPushButton:pressed {
                    background-color: #2C5F7F;
                }
                QPushButton:disabled {
                    background-color: #CCCCCC;
                    color: #666666;
                }
                
                /* Cards have subtle border instead of different background */
                QFrame.card {
                    background-color: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                }
                
                QFrame.card QLabel.card-title {
                    color: #4FA1D8;
                    font-weight: bold;
                    background-color: transparent;
                }
                
                QFrame.card QLabel.card-description {
                    color: #666666;
                    background-color: transparent;
                }
                
                QFrame#activityIndicator {
                    background-color: #4FA1D8;
                    border-radius: 6px;
                    
                }
                
                QLabel#status, QLabel#credits {
                    color: #666666;
                    
                }
                QFrame#header QLabel, QFrame#header QWidget {
                    background-color: transparent;
                }
                QFrame.card QLabel, QFrame.card QHBoxLayout, QFrame.card QVBoxLayout {
                    background-color: transparent;
                }
            """)
        
        # Create blinking animation for the activity indicator
        activity_indicator = self.findChild(QFrame, "activityIndicator")
        if activity_indicator:
            self.activity_timer = QTimer(self)
            self.activity_timer.timeout.connect(lambda: self.toggle_activity_indicator(activity_indicator))
            self.activity_timer.start(1000)  # Blink every second
    
    def toggle_activity_indicator(self, indicator):
        # Toggle visibility for blinking effect
        if indicator.isVisible():
            indicator.hide()
        else:
            indicator.show()
        
    def toggle_theme(self):
        self.dark_mode = self.theme_toggle.isChecked()
        self.apply_theme()
        
    def create_improved_card(self, title, icon, description, button_text, button_function, enabled=True):
        card = QFrame()
        card.setProperty("class", "card")
        card.setMinimumHeight(250)  # Taller to accommodate description
        
        # Card layout
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Icon and title in horizontal layout
        header_layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 22))
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setProperty("class", "card-title")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Description - NEW ELEMENT
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setProperty("class", "card-description")
        desc_label.setMinimumHeight(60)
        
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Button with consistent styling
        button = QPushButton(button_text)
        button.setMinimumHeight(45)
        button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(button_function)
        button.setEnabled(enabled)
         
        if not enabled:
            disabled_label = QLabel("Module not available")
            disabled_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            disabled_label.setFont(QFont("Segoe UI", 9))
            disabled_label.setStyleSheet("color: #888888;")
            layout.addWidget(disabled_label)
        
        layout.addWidget(button)
        
        # Add subtle shadow effect to the card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(2, 2)
        card.setGraphicsEffect(shadow)
        
        return card

    def open_simulator(self):
        try:
            self.simulator_window = DeadlockDetectorGUI()
            self.simulator_window.show()
        except Exception as e:
            self.show_enhanced_error_message(f"Error launching simulator: {e}")
    
    def open_detector(self):
        try:
            if ai_module_available:
                self.detector_window = pa.DeadlockDetectorGUI1()
                self.detector_window.show()
            else:
                self.show_enhanced_error_message("AI-powered deadlock detector module is not available.")
        except Exception as e:
            self.show_enhanced_error_message(f"Error launching detector: {e}")
    
    def show_enhanced_error_message(self, message):
        # Create an enhanced error dialog
        error_dialog = QFrame(self)
        error_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        error_dialog.setFixedSize(440, 200)
        
         
        if self.dark_mode:
            error_dialog.setStyleSheet("""
                background-color: #252525;
                border: 2px solid #FF5252;
                border-radius: 10px;
            """)
        else:
            error_dialog.setStyleSheet("""
                background-color: white;
                border: 2px solid #FF5252;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            """)
            
         
        parent_center = self.mapToGlobal(self.rect().center())
        error_dialog.move(parent_center.x() - 220, parent_center.y() - 100)
        
        layout = QVBoxLayout(error_dialog)
        layout.setSpacing(15)
        
        
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Segoe UI", 18))
        
        title = QLabel("Error Detected")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #FF5252;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
    
        msg_frame = QFrame()
        msg_frame.setStyleSheet(f"""
            background-color: {'#2D2D2D' if self.dark_mode else '#F8F8F8'};
            border-radius: 6px;
            padding: 10px;
        """)
        
        msg_layout = QVBoxLayout(msg_frame)
        
        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        msg.setStyleSheet(f"color: {'#F0F0F0' if self.dark_mode else '#333333'};")
        msg.setTextFormat(Qt.TextFormat.RichText)
        
        msg_layout.addWidget(msg)
        
        # Button with better styling
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Dismiss")
        close_btn.setMinimumWidth(120)
        close_btn.setMinimumHeight(40)
        close_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5252;
                color: white;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #FF7070;
            }
            QPushButton:pressed {
                background-color: #E04545;
            }
        """)
        close_btn.clicked.connect(error_dialog.close)
        
        button_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        layout.addWidget(msg_frame)
        layout.addLayout(button_layout)
        
        # Apply shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 6)
        error_dialog.setGraphicsEffect(shadow)
        
        error_dialog.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    main_gui.show()
    sys.exit(app.exec())
