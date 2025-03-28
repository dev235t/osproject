import sys
import google.generativeai as genai
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, 
    QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, 
    QComboBox, QGroupBox, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# 🔥 PLACE YOUR GEMINI API KEY HERE 🔥
API_KEY = "AIzaSyBTa3KtZHgwxzDxQq2hUtOrNKq4ulmuZ2I"
genai.configure(api_key=API_KEY)

class DeadlockDetectorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.processes = []
        self.resources = {}
        self.allocations = []
        self.requests = []
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("⚙️ AI Deadlock Detector 🔍")
        self.setGeometry(100, 100, 1500, 900)
        self.setStyleSheet("background-color: #000000; color: white;")

        main_layout = QVBoxLayout()
        
        # Process & Resource Input (Side by Side)
        input_layout = QHBoxLayout()
        
        # Process Group
        process_group = QGroupBox("➕ Add Process")
        process_group.setStyleSheet("font-size: 14px; padding: 5px;")
        process_layout = QVBoxLayout()
        self.process_input = QLineEdit(self)
        self.process_input.setPlaceholderText("Enter Process Name")
        self.add_process_button = QPushButton("✅ Add Process")
        self.add_process_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-size: 14px;")
        self.add_process_button.clicked.connect(self.add_process)
        process_layout.addWidget(self.process_input)
        process_layout.addWidget(self.add_process_button)
        process_group.setLayout(process_layout)
        
        # Resource Group
        resource_group = QGroupBox("🔗 Add Resource")
        resource_group.setStyleSheet("font-size: 14px; padding: 9px;")
        resource_layout = QVBoxLayout()
        self.resource_input = QLineEdit(self)
        self.resource_input.setPlaceholderText("Enter Resource Name")
        self.resource_count_input = QLineEdit(self)
        self.resource_count_input.setPlaceholderText("Total Instances")
        self.add_resource_button = QPushButton("➕ Add Resource")
        self.add_resource_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-size: 14px;")
        self.add_resource_button.clicked.connect(self.add_resource)
        resource_layout.addWidget(self.resource_input)
        resource_layout.addWidget(self.resource_count_input)
        resource_layout.addWidget(self.add_resource_button)
        resource_group.setLayout(resource_layout)

        input_layout.addWidget(process_group)
        input_layout.addWidget(resource_group)
        main_layout.addLayout(input_layout)
        
        # Allocation & Request Section
        alloc_group = QGroupBox("🔄 Resource Allocation & Request")
        alloc_group.setStyleSheet("padding: 10px;")
        alloc_layout = QGridLayout()

        # Common dropdowns for both allocation and request
        self.alloc_process_dropdown = QComboBox(self)
        self.alloc_resource_dropdown = QComboBox(self)
        self.alloc_count_input = QLineEdit(self)
        self.alloc_count_input.setPlaceholderText("Count")

        # Allocate Resource Button
        self.add_alloc_button = QPushButton("🔗 Allocate Resource")
        self.add_alloc_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-size: 14px;")
        self.add_alloc_button.clicked.connect(self.add_allocation)

        # Request Resource Button
        self.request_resource_button = QPushButton("🆘 Request Resource")
        self.request_resource_button.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; font-size: 14px;")
        self.request_resource_button.clicked.connect(self.request_resource)

        # Layout setup
        alloc_layout.addWidget(QLabel("🖥 Process:"), 0, 0)
        alloc_layout.addWidget(self.alloc_process_dropdown, 0, 1)
        alloc_layout.addWidget(QLabel("🔧 Resource:"), 0, 2)
        alloc_layout.addWidget(self.alloc_resource_dropdown, 0, 3)
        alloc_layout.addWidget(QLabel("🔢 Count:"), 0, 4)
        alloc_layout.addWidget(self.alloc_count_input, 0, 5)
        alloc_layout.addWidget(self.add_alloc_button, 0, 6)
        alloc_layout.addWidget(self.request_resource_button, 0, 7)

        alloc_group.setLayout(alloc_layout)
        main_layout.addWidget(alloc_group)
        
      
        # Horizontal layout to hold the table and empty group
        table_layout = QHBoxLayout()

        # Table to display process allocations and requests
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["🆔 ID", "🖥 Process", "🔧 Resource", "📌 Status"])
        self.table.setStyleSheet("background-color: #222; color: white;")
        self.table.horizontalHeader().setDefaultSectionSize(180)  # Adjust column width  
        table_layout.addWidget(self.table)

        # Empty Group Box for spacing or future use
        empty_group = QGroupBox("⚡ Empty Space")
        empty_group.setStyleSheet("border: 2px dashed white; padding: 10px; width: 700px;")
        table_layout.addWidget(empty_group)

        main_layout.addLayout(table_layout)

        
        # Response Output Box
        self.response_box = QTextEdit(self)
        self.response_box.setReadOnly(True)
        self.response_box.setStyleSheet("background-color: #222; color: #0f0; font-size: 14px; padding: 5px;")
        main_layout.addWidget(self.response_box)
        
        # Manual Deadlock Detection Button
        self.detect_button = QPushButton("⚠️ Detect Deadlock", self)
        self.detect_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.detect_button.setStyleSheet("background-color: #dc3545; color: white; padding: 12px; border-radius: 8px;")
        self.detect_button.clicked.connect(self.detect_deadlock)
        main_layout.addWidget(self.detect_button)
        
        self.setLayout(main_layout)
    def add_process(self):
        process_name = self.process_input.text().strip()
        if process_name and process_name not in self.processes:
            self.processes.append(process_name)
            self.alloc_process_dropdown.addItem(process_name)
            self.process_input.clear()

    def add_resource(self):
        resource_name = self.resource_input.text().strip()
        total_instances = self.resource_count_input.text().strip()
        if resource_name and total_instances.isdigit():
            self.resources[resource_name] = int(total_instances)
            self.alloc_resource_dropdown.addItem(resource_name)
            self.resource_input.clear()
            self.resource_count_input.clear()

    def add_allocation(self):
        self.update_table("ALLOCATED")
        process = self.alloc_process_dropdown.currentText()
        resource = self.alloc_resource_dropdown.currentText()
        count = self.alloc_count_input.text().strip()
        if process and resource and count.isdigit():
            self.allocations.append((process, resource, int(count)))

    def request_resource(self):
        self.update_table("REQUESTED")
        process = self.alloc_process_dropdown.currentText()
        resource = self.alloc_resource_dropdown.currentText()
        count = self.alloc_count_input.text().strip()
        if process and resource and count.isdigit():
            self.requests.append((process, resource, int(count)))


    def update_table(self, action):
        process = self.alloc_process_dropdown.currentText()
        resource = self.alloc_resource_dropdown.currentText()
        count = self.alloc_count_input.text().strip()
        if process and resource and count.isdigit():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))
            self.table.setItem(row_position, 1, QTableWidgetItem(process))
            self.table.setItem(row_position, 2, QTableWidgetItem(resource))
            self.table.setItem(row_position, 3, QTableWidgetItem(f"{count} ({action})"))

    def detect_deadlock(self):
        prompt = f"Analyze this allocation & requests for deadlock and suggest updates while also visualising deadlock cycle:\nAllocations: {self.allocations}\nRequests: {self.requests}"
        try:
            response = genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt)
            self.response_box.setText(response.text)
        except Exception as e:
            self.response_box.setText(f"Error detecting deadlock: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DeadlockDetectorGUI()
    gui.show()
    sys.exit(app.exec())
