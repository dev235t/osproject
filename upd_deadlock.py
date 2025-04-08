import sys
import google.generativeai as genai
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, 
    QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, 
    QComboBox, QGroupBox, QGridLayout, QSplitter, QFrame, QHeaderView,
    QTabWidget, QScrollArea
)
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QPixmap
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve

 
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
        
        # Set modern dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 12px;
                font-size: 14px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #004c8c;
            }
            QLineEdit {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                background-color: #252525;
                color: #e0e0e0;
            }
            QComboBox {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                background-color: #252525;
                color: #e0e0e0;
            }
            QTableWidget {
                background-color: #252525;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                gridline-color: #3a3a3a;
                selection-background-color: #0078d7;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                padding: 8px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #252525;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                color: #00ff00;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d7;
                color: white;
            }
            QScrollBar {
                background-color: #252525;
                width: 12px;
                height: 12px;
            }
            QScrollBar::handle {
                background-color: #444444;
                border-radius: 6px;
            }
            QScrollBar::handle:hover {
                background-color: #555555;
            }
        """)

        main_layout = QVBoxLayout()
        
        # Header with app name and description
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #0078d7; border-radius: 6px;")
        header_layout = QHBoxLayout(header_frame)
        
        app_title = QLabel("AI Deadlock Detector")
        app_title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        app_description = QLabel("Detect and analyze resource allocation deadlocks with AI assistance")
        app_description.setStyleSheet("font-size: 14px; color: white;")
        
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(app_description)
        
        main_layout.addWidget(header_frame)
        
        # Tabs for different sections
        tab_widget = QTabWidget()
        
        # Tab 1: Setup Resources & Processes
        setup_tab = QWidget()
        setup_layout = QVBoxLayout(setup_tab)
        
        # Process & Resource Input (Side by Side)
        input_layout = QHBoxLayout()
        
        # Process Group
        process_group = QGroupBox("➕ Processes")
        process_layout = QVBoxLayout()
        
        process_label = QLabel("Define system processes")
        process_label.setStyleSheet("color: #0078d7;")
        
        self.process_input = QLineEdit(self)
        self.process_input.setPlaceholderText("Enter Process Name (e.g., P1, Process_A)")
        
        self.add_process_button = QPushButton("✅ Add Process")
        self.add_process_button.clicked.connect(self.add_process)
        
        # Process list display
        self.process_list = QTextEdit()
        self.process_list.setReadOnly(True)
        self.process_list.setMaximumHeight(120)
        self.process_list.setPlaceholderText("Added processes will appear here")
        
        process_layout.addWidget(process_label)
        process_layout.addWidget(self.process_input)
        process_layout.addWidget(self.add_process_button)
        process_layout.addWidget(QLabel("Current Processes:"))
        process_layout.addWidget(self.process_list)
        process_group.setLayout(process_layout)
        
        # Resource Group
        resource_group = QGroupBox("🔗 Resources")
        resource_layout = QVBoxLayout()
        
        resource_label = QLabel("Define system resources")
        resource_label.setStyleSheet("color: #0078d7;")
        
        resource_form_layout = QGridLayout()
        self.resource_input = QLineEdit(self)
        self.resource_input.setPlaceholderText("Enter Resource Name (e.g., R1, Printer)")
        
        self.resource_count_input = QLineEdit(self)
        self.resource_count_input.setPlaceholderText("Total Instances (e.g., 1, 2, 3)")
        
        resource_form_layout.addWidget(QLabel("Resource Name:"), 0, 0)
        resource_form_layout.addWidget(self.resource_input, 0, 1)
        resource_form_layout.addWidget(QLabel("Instances:"), 1, 0)
        resource_form_layout.addWidget(self.resource_count_input, 1, 1)
        
        self.add_resource_button = QPushButton("➕ Add Resource")
        self.add_resource_button.clicked.connect(self.add_resource)
        
        # Resource list display
        self.resource_list = QTextEdit()
        self.resource_list.setReadOnly(True)
        self.resource_list.setMaximumHeight(120)
        self.resource_list.setPlaceholderText("Added resources will appear here")
        
        resource_layout.addWidget(resource_label)
        resource_layout.addLayout(resource_form_layout)
        resource_layout.addWidget(self.add_resource_button)
        resource_layout.addWidget(QLabel("Current Resources:"))
        resource_layout.addWidget(self.resource_list)
        resource_group.setLayout(resource_layout)

        input_layout.addWidget(process_group)
        input_layout.addWidget(resource_group)
        setup_layout.addLayout(input_layout)
        
        tab_widget.addTab(setup_tab, "🛠️ Setup")
        
        # Tab 2: Allocation & Requests
        alloc_tab = QWidget()
        alloc_layout = QVBoxLayout(alloc_tab)
        
        # Allocation & Request Section
        alloc_group = QGroupBox("🔄 Resource Allocation & Request")
        alloc_inner_layout = QVBoxLayout()
        
        instruction_label = QLabel("Define how processes are using or requesting resources")
        instruction_label.setStyleSheet("color: #0078d7; margin-bottom: 10px;")
        alloc_inner_layout.addWidget(instruction_label)

        form_layout = QGridLayout()
        
        # Process dropdown
        form_layout.addWidget(QLabel("🖥️ Process:"), 0, 0)
        self.alloc_process_dropdown = QComboBox(self)
        self.alloc_process_dropdown.setMinimumWidth(150)
        form_layout.addWidget(self.alloc_process_dropdown, 0, 1)
        
        # Resource dropdown
        form_layout.addWidget(QLabel("🔧 Resource:"), 0, 2)
        self.alloc_resource_dropdown = QComboBox(self)
        self.alloc_resource_dropdown.setMinimumWidth(150)
        form_layout.addWidget(self.alloc_resource_dropdown, 0, 3)
        
        # Count input
        form_layout.addWidget(QLabel("🔢 Count:"), 0, 4)
        self.alloc_count_input = QLineEdit(self)
        self.alloc_count_input.setPlaceholderText("Number of instances")
        self.alloc_count_input.setMaximumWidth(150)
        form_layout.addWidget(self.alloc_count_input, 0, 5)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_alloc_button = QPushButton("🔗 Allocate Resource")
        self.add_alloc_button.clicked.connect(self.add_allocation)
        
        self.request_resource_button = QPushButton("🆘 Request Resource")
        self.request_resource_button.clicked.connect(self.request_resource)
        
        button_layout.addWidget(self.add_alloc_button)
        button_layout.addWidget(self.request_resource_button)
        
        alloc_inner_layout.addLayout(form_layout)
        alloc_inner_layout.addLayout(button_layout)
        alloc_group.setLayout(alloc_inner_layout)
        alloc_layout.addWidget(alloc_group)
        
        # Table improved layout
        table_group = QGroupBox("📊 Current System State")
        table_layout = QVBoxLayout()
        
        # Enhanced table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["🆔 ID", "🖥️ Process", "🔧 Resource", "🔢 Count", "📌 Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #2a2a2a;")
        
        # Table controls
        table_controls = QHBoxLayout()
        clear_table_button = QPushButton("🗑️ Clear Table")
        clear_table_button.clicked.connect(self.clear_table)
        clear_table_button.setStyleSheet("background-color: #d83131;")
        
        export_button = QPushButton("💾 Export Data")
        export_button.clicked.connect(self.export_data)
        
        table_controls.addWidget(clear_table_button)
        table_controls.addWidget(export_button)
        
        table_layout.addWidget(self.table)
        table_layout.addLayout(table_controls)
        table_group.setLayout(table_layout)
        
        alloc_layout.addWidget(table_group)
        tab_widget.addTab(alloc_tab, "📝 Allocations")
        
        # Tab 3: Analysis
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Response Output Box with improved formatting
        response_group = QGroupBox("🧠 AI Analysis")
        response_layout = QVBoxLayout()
        
        analysis_instruction = QLabel("Click 'Detect Deadlock' to analyze the current system state using AI")
        analysis_instruction.setStyleSheet("color: #0078d7; margin-bottom: 10px;")
        
        self.response_box = QTextEdit(self)
        self.response_box.setReadOnly(True)
        self.response_box.setMinimumHeight(300)
        self.response_box.setPlaceholderText("AI analysis results will appear here...")
        
        # Manual Deadlock Detection Button
        self.detect_button = QPushButton("⚠️ Detect Deadlock", self)
        self.detect_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.detect_button.setStyleSheet("""
            background-color: #dc3545; 
            color: white; 
            padding: 12px; 
            border-radius: 8px;
            height: 50px;
        """)
        self.detect_button.clicked.connect(self.detect_deadlock)
        
        # Additional analysis tools
        analysis_tools = QHBoxLayout()
        
        save_report_button = QPushButton("📊 Save Report")
        save_report_button.clicked.connect(self.save_report)
        
        clear_analysis_button = QPushButton("🧹 Clear Analysis")
        clear_analysis_button.clicked.connect(self.clear_analysis)
        
        analysis_tools.addWidget(save_report_button)
        analysis_tools.addWidget(clear_analysis_button)
        
        response_layout.addWidget(analysis_instruction)
        response_layout.addWidget(self.response_box)
        response_layout.addWidget(self.detect_button)
        response_layout.addLayout(analysis_tools)
        response_group.setLayout(response_layout)
        
        analysis_layout.addWidget(response_group)
        tab_widget.addTab(analysis_tab, "🔍 Analysis")
        
        # Add tabs to main layout
        main_layout.addWidget(tab_widget)
        
        # Status footer
        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: #252525; border-radius: 4px;")
        footer_layout = QHBoxLayout(footer_frame)
        
        status_label = QLabel("Status: Ready")
        status_label.setStyleSheet("color: #00ff00;")
        
        version_label = QLabel("v1.2.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        footer_layout.addWidget(status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(version_label)
        
        main_layout.addWidget(footer_frame)
        
        self.setLayout(main_layout)

    def add_process(self):
        process_name = self.process_input.text().strip()
        if process_name and process_name not in self.processes:
            self.processes.append(process_name)
            self.alloc_process_dropdown.addItem(process_name)
            self.process_input.clear()
            
            # Update process list display
            self.process_list.setText("\n".join(self.processes))
            
            # Show success message
            QMessageBox.information(self, "Success", f"Process '{process_name}' added successfully!")

    def add_resource(self):
        resource_name = self.resource_input.text().strip()
        total_instances = self.resource_count_input.text().strip()
        if resource_name and total_instances.isdigit():
            self.resources[resource_name] = int(total_instances)
            self.alloc_resource_dropdown.addItem(resource_name)
            self.resource_input.clear()
            self.resource_count_input.clear()
            
            # Update resource list display
            resource_text = "\n".join([f"{r}: {c} instances" for r, c in self.resources.items()])
            self.resource_list.setText(resource_text)
            
            # Show success message
            QMessageBox.information(self, "Success", f"Resource '{resource_name}' with {total_instances} instances added successfully!")

    def add_allocation(self):
        process = self.alloc_process_dropdown.currentText()
        resource = self.alloc_resource_dropdown.currentText()
        count = self.alloc_count_input.text().strip()
        if process and resource and count.isdigit():
            self.allocations.append((process, resource, int(count)))
            self.update_table(process, resource, count, "ALLOCATED")
            self.alloc_count_input.clear()

    def request_resource(self):
        process = self.alloc_process_dropdown.currentText()
        resource = self.alloc_resource_dropdown.currentText()
        count = self.alloc_count_input.text().strip()
        if process and resource and count.isdigit():
            self.requests.append((process, resource, int(count)))
            self.update_table(process, resource, count, "REQUESTED")
            self.alloc_count_input.clear()

    

    def update_table(self, process, resource, count, action):
        if process and resource and count.isdigit():
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # Set items with proper alignment and formatting
            id_item = QTableWidgetItem(str(row_position + 1))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            process_item = QTableWidgetItem(process)
            resource_item = QTableWidgetItem(resource)
            
            count_item = QTableWidgetItem(count)
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_item = QTableWidgetItem(action)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Set background color based on action
            if action == "ALLOCATED":
                status_item.setBackground(QColor("#28a745"))
            else:
                status_item.setBackground(QColor("#ffc107"))
            
            self.table.setItem(row_position, 0, id_item)
            self.table.setItem(row_position, 1, process_item)
            self.table.setItem(row_position, 2, resource_item)
            self.table.setItem(row_position, 3, count_item)
            self.table.setItem(row_position, 4, status_item)

    def detect_deadlock(self):
        if not self.allocations and not self.requests:
            QMessageBox.warning(self, "Warning", "No allocations or requests defined. Please add some data first.")
            return
            
        # Show loading indicator
        self.response_box.setText("Analyzing deadlock situation... Please wait...")
        QApplication.processEvents()
        
        prompt = f"""
        Analyze this allocation & requests for deadlock and suggest updates:
        
        Processes: {self.processes}
        Resources: {self.resources}
        
        Allocations: {self.allocations}
        Requests: {self.requests}
        
        Please provide:
        1. Whether a deadlock exists
        2. If so, identify the deadlock cycle
        3. Visualization of the deadlock (as ASCII art)
        4. Recommendations to resolve the deadlock
        """
        
        try:
            response = genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt)
            self.response_box.setText(response.text)
        except Exception as e:
            self.response_box.setText(f"Error detecting deadlock: {str(e)}")

    def clear_table(self):
        # Clear the table and underlying data
        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to clear all allocation and request data?", 
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.table.setRowCount(0)
            self.allocations = []
            self.requests = []

    def export_data(self):
        """
        Exports the current allocation and request data to a text file.
        Includes processes, resources, allocations, and requests.
        """
        try:
            from PyQt6.QtWidgets import QFileDialog
            import datetime
            
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Data", 
                f"deadlock_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt)"
            )
            
            if not file_path:  # User canceled
                return
                
            with open(file_path, 'w') as file:
                # Write header
                file.write("=" * 50 + "\n")
                file.write("DEADLOCK DETECTOR - SYSTEM STATE EXPORT\n")
                file.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("=" * 50 + "\n\n")
                
                # Write processes
                file.write("PROCESSES:\n")
                if self.processes:
                    for i, process in enumerate(self.processes, 1):
                        file.write(f"{i}. {process}\n")
                else:
                    file.write("No processes defined.\n")
                file.write("\n")
                
                # Write resources
                file.write("RESOURCES:\n")
                if self.resources:
                    for i, (resource, count) in enumerate(self.resources.items(), 1):
                        file.write(f"{i}. {resource}: {count} instances\n")
                else:
                    file.write("No resources defined.\n")
                file.write("\n")
                
                # Write allocations
                file.write("RESOURCE ALLOCATIONS:\n")
                if self.allocations:
                    for i, (process, resource, count) in enumerate(self.allocations, 1):
                        file.write(f"{i}. Process {process} has allocated {count} instance(s) of {resource}\n")
                else:
                    file.write("No allocations defined.\n")
                file.write("\n")
                
                # Write requests
                file.write("RESOURCE REQUESTS:\n")
                if self.requests:
                    for i, (process, resource, count) in enumerate(self.requests, 1):
                        file.write(f"{i}. Process {process} is requesting {count} instance(s) of {resource}\n")
                else:
                    file.write("No requests defined.\n")
                file.write("\n")
                
                # Write table data
                file.write("SYSTEM STATE TABLE:\n")
                if self.table.rowCount() > 0:
                    headers = ["ID", "Process", "Resource", "Count", "Status"]
                    header_line = f"{headers[0]:<5} | {headers[1]:<10} | {headers[2]:<10} | {headers[3]:<5} | {headers[4]:<10}"
                    file.write(header_line + "\n")
                    file.write("-" * len(header_line) + "\n")
                    
                    for row in range(self.table.rowCount()):
                        id_val = self.table.item(row, 0).text()
                        process = self.table.item(row, 1).text()
                        resource = self.table.item(row, 2).text()
                        count = self.table.item(row, 3).text()
                        status = self.table.item(row, 4).text()
                        
                        file.write(f"{id_val:<5} | {process:<10} | {resource:<10} | {count:<5} | {status:<10}\n")
                else:
                    file.write("No data in table.\n")
                    
            QMessageBox.information(self, "Export Successful", f"Data successfully exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting data: {str(e)}")

    def save_report(self):
        """
        Saves the current AI analysis report to a text file.
        """
        try:
            from PyQt6.QtWidgets import QFileDialog
            import datetime
            
            # Check if there's content to save
            if not self.response_box.toPlainText().strip():
                QMessageBox.warning(self, "Save Report", "No analysis results to save. Please run deadlock detection first.")
                return
                
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Analysis Report", 
                f"deadlock_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt)"
            )
            
            if not file_path:  # User canceled
                return
                
            with open(file_path, 'w') as file:
                # Write header
                file.write("=" * 60 + "\n")
                file.write("DEADLOCK DETECTOR - AI ANALYSIS REPORT\n")
                file.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("=" * 60 + "\n\n")
                
                # Write system state summary
                file.write("SYSTEM STATE SUMMARY:\n")
                file.write(f"- Total Processes: {len(self.processes)}\n")
                file.write(f"- Total Resources: {len(self.resources)}\n")
                file.write(f"- Total Allocations: {len(self.allocations)}\n")
                file.write(f"- Total Requests: {len(self.requests)}\n\n")
                
                # Write processes
                file.write("PROCESSES: " + ", ".join(self.processes) + "\n\n")
                
                # Write resources
                resources_str = ", ".join([f"{r} ({c} instances)" for r, c in self.resources.items()])
                file.write("RESOURCES: " + resources_str + "\n\n")
                
                # Write analysis report
                file.write("AI ANALYSIS REPORT:\n")
                file.write("-" * 60 + "\n")
                file.write(self.response_box.toPlainText())
                file.write("\n\n")
                
                # Write footer
                file.write("-" * 60 + "\n")
                file.write("End of Report\n")
                    
            QMessageBox.information(self, "Save Successful", f"Analysis report successfully saved to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving report: {str(e)}")

    def clear_analysis(self):
        # Clear the analysis text
        self.response_box.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DeadlockDetectorGUI()
    gui.show()
    sys.exit(app.exec())
