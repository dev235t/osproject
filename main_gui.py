import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from upd_deadlock import DeadlockDetectorGUI  # Import your existing GUI

class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Main Menu")
        self.setGeometry(300, 300, 400, 200)
        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout()

        self.start_button = QPushButton("🛠 Deadlock Simulator")
        self.start_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-size: 14px;")
        self.start_button.clicked.connect(self.open_simulator)

        layout.addWidget(self.start_button)
        self.setLayout(layout)

    def open_simulator(self):
        self.simulator_window = DeadlockDetectorGUI()
        self.simulator_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    main_gui.show()
    sys.exit(app.exec())
