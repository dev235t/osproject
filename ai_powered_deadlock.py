import sys
import psutil
import google.generativeai as genai
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
                            QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, 
                            QHBoxLayout, QHeaderView, QSplitter, QFrame)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


API_KEY = "AIzaSyCxC5CUgTq9ggXTtUZp0Nd9gDaHxr-bf_A"
genai.configure(api_key=API_KEY)

class FetchProcessesThread(QThread):
    result_signal = pyqtSignal(list)
    
    def run(self):
        process_data = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'num_threads']):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    num_threads = proc.info['num_threads']
                    
                    # More comprehensive CPU usage calculation
                    try:
                        # First call might return 0, so we'll do multiple measurements
                        cpu_usages = []
                        for _ in range(3):
                            cpu_usage = proc.cpu_percent(interval=0.1)
                            cpu_usages.append(cpu_usage)
                        
                        # Take the maximum or average of measurements
                        cpu_usage = max(cpu_usages)
                    except Exception as e:
                        print(f"CPU usage error for {name}: {e}")
                        cpu_usage = 0.0
                    
                    with proc.oneshot():
                        status = proc.status()
                        memory_usage = proc.memory_info().rss // (1024 * 1024)  # in MB
                        
                        # Safer file handle counting
                        try:
                            allocated_resources = f"File Handles: {len(proc.open_files())}" if proc.open_files() else "None"
                        except Exception:
                            allocated_resources = "Unable to count file handles"
                        
                        requested_resources = f"Memory: {memory_usage}MB, CPU: {cpu_usage}%"
                        
                        process_data.append({
                            'pid': pid,
                            'name': name,
                            'status': status,
                            'num_threads': num_threads,
                            'memory_usage': memory_usage,
                            'cpu_usage': cpu_usage,
                            'allocated_resources': allocated_resources,
                            'requested_resources': requested_resources
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        
        except Exception as e:
            print(f"Error in process collection: {e}")
        
        # Sort processes by CPU usage in descending order
        process_data.sort(key=lambda x: x['cpu_usage'], reverse=True)
        
        self.result_signal.emit(process_data)
        
class DeadlockDetectionThread(QThread):
    result_signal = pyqtSignal(str)
    
    def __init__(self, process_data):
        super().__init__()
        self.process_data = process_data
    
    def run(self):
        try:
            prompt = "Given the following process allocation and request information, identify if there is a deadlock:\n" + \
                     "Process Information:\n" + \
                     "\n".join([f"PID: {proc['pid']}, Name: {proc['name']}, Status: {proc['status']}, Threads: {proc['num_threads']}, " +
                                f"Memory Usage: {proc['memory_usage']}MB, CPU Usage: {proc['cpu_usage']}%, " +
                                f"Allocated Resources: {proc['allocated_resources']}, Requested Resources: {proc['requested_resources']}" 
                                for proc in self.process_data])
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            self.result_signal.emit(response.text)
        except Exception as e:
            self.result_signal.emit(f"Error: {str(e)}")


class DeadlockDetectorGUI1(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Set up main window properties
        self.setWindowTitle("⚙️ AI Deadlock Detector 🔍")
        self.setGeometry(100, 100, 1400, 700)
        
        # Define color scheme
        self.bg_color = "#121212"
        self.secondary_bg = "#1E1E1E"
        self.accent_color = "#03DAC5"
        self.danger_color = "#CF6679"
        self.success_color = "#4CAF50"
        self.text_color = "#FFFFFF"
        self.header_color = "#BB86FC"
        
        # Create and apply stylesheet
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.bg_color};
                color: {self.text_color};
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton {{
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            QTableWidget {{
                background-color: {self.secondary_bg};
                alternate-background-color: {self.bg_color};
                gridline-color: #333333;
                border: 1px solid #333333;
                border-radius: 4px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {self.secondary_bg};
                color: {self.header_color};
                padding: 8px;
                border: 1px solid #333333;
                font-weight: bold;
            }}
            QTextEdit {{
                background-color: {self.secondary_bg};
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            QProgressBar {{
                border: 1px solid #333333;
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {self.accent_color};
            }}
        """)

        # Create main layout with splitter
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left widget for process list and graph
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # App title and description
        header_layout = QHBoxLayout()
        title_label = QLabel("AI Deadlock Detector")
        title_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.accent_color};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        left_layout.addLayout(header_layout)
        
        desc_label = QLabel("Monitor system processes and detect potential deadlocks using AI")
        desc_label.setStyleSheet("font-size: 14px; color: #BBBBBB; margin-bottom: 10px;")
        left_layout.addWidget(desc_label)
        
        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(8)
        self.process_table.setHorizontalHeaderLabels([
            " 🔢 S.No ", 
            " 🆔 PID ", 
            " 📝 Process Name ", 
            " ⚡ Status ", 
            " 🧵 Threads ", 
            " 💾 Memory ", 
            " 📦 Allocated ", 
            " 📥 Requested "
        ])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.process_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setShowGrid(True)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        left_layout.addWidget(self.process_table)
        
        # Progress bar for loading indication
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setMaximumHeight(6)
        self.loading_bar.hide()
        left_layout.addWidget(self.loading_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Fetch processes button
        self.get_process_button = QPushButton("🔄 Fetch Processes")
        self.get_process_button.setStyleSheet(f"background-color: {self.accent_color}; color: #000000;")
        self.get_process_button.clicked.connect(self.fetch_processes)
        button_layout.addWidget(self.get_process_button)
        
        # Show graph button
        self.show_graph_button = QPushButton("📊 Update Graph")
        self.show_graph_button.setStyleSheet(f"background-color: {self.success_color}; color: #000000;")
        self.show_graph_button.clicked.connect(self.manual_graph_update)
        button_layout.addWidget(self.show_graph_button)
        
        left_layout.addLayout(button_layout)
        
        # Graph section with title
        graph_frame = QFrame()
        graph_frame.setStyleSheet(f"background-color: {self.secondary_bg}; border-radius: 4px;")
        graph_layout = QVBoxLayout(graph_frame)
        
        graph_title = QLabel("Memory Usage by Process")
        graph_title.setStyleSheet(f"color: {self.header_color}; font-weight: bold; font-size: 16px;")
        graph_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_layout.addWidget(graph_title)
        
        # Set up matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor(self.secondary_bg)
        self.ax_threads = self.figure.add_subplot(111)
        self.ax_threads.set_facecolor(self.secondary_bg)
        
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)
        left_layout.addWidget(graph_frame)
        
        # Right widget for deadlock detection
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Deadlock section title
        deadlock_title = QLabel("Deadlock Analysis")
        deadlock_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.header_color};")
        right_layout.addWidget(deadlock_title)
        
        # Deadlock detection button
        self.detect_deadlock_button = QPushButton("🚨 Detect Deadlocks")
        self.detect_deadlock_button.setStyleSheet(f"background-color: {self.danger_color}; color: #000000;")
        self.detect_deadlock_button.setMinimumHeight(50)
        self.detect_deadlock_button.clicked.connect(self.detect_deadlock)
        right_layout.addWidget(self.detect_deadlock_button)
        
        # Deadlock response section
        response_frame = QFrame()
        response_frame.setStyleSheet(f"background-color: {self.secondary_bg}; border-radius: 4px;")
        response_layout = QVBoxLayout(response_frame)
        
        response_title = QLabel("AI Analysis Results")
        response_title.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        response_layout.addWidget(response_title)
        
        self.deadlock_response = QTextEdit()
        self.deadlock_response.setReadOnly(True)
        self.deadlock_response.setPlaceholderText("AI analysis will appear here...")
        response_layout.addWidget(self.deadlock_response)
        
        right_layout.addWidget(response_frame)
        
        # Status information section
        status_frame = QFrame()
        status_frame.setStyleSheet(f"background-color: {self.secondary_bg}; border-radius: 4px; padding: 10px;")
        status_layout = QVBoxLayout(status_frame)
        
        status_title = QLabel("System Status")
        status_title.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        status_layout.addWidget(status_title)
        
        # Add system status information
        status_info = QLabel("• Fetch processes to monitor system activity\n• Select processes for detailed information\n• Use AI to detect potential deadlocks")
        status_info.setStyleSheet("color: #BBBBBB;")
        status_layout.addWidget(status_info)
        
        right_layout.addWidget(status_frame)
        right_layout.addStretch()
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([2*self.width()//3, self.width()//3])  # 2:1 ratio
        
    def fetch_processes(self):
        self.loading_bar.show()
        self.get_process_button.setEnabled(False)
        self.get_process_button.setText("⏳ Loading...")
        QApplication.processEvents()
        
        self.process_thread = FetchProcessesThread()
        self.process_thread.result_signal.connect(self.update_process_table)
        self.process_thread.start()
    
    def update_process_table(self, process_data):
        self.loading_bar.hide()
        self.get_process_button.setEnabled(True)
        self.get_process_button.setText("🔄 Fetch Processes")
        
        self.process_table.setRowCount(0)
        for i, proc in enumerate(process_data):
            row = self.process_table.rowCount()
            self.process_table.insertRow(row)
            
            # Color high CPU usage rows with a subtle indicator
            cpu_usage = proc['cpu_usage']
            row_color = None
            if cpu_usage > 50:
                row_color = QColor(80, 0, 0, 40)  # Red with transparency
            elif cpu_usage > 20:
                row_color = QColor(80, 80, 0, 40)  # Yellow with transparency
                
            # Add items to the row
            for col, value in enumerate([
                str(i + 1),
                str(proc['pid']),
                proc['name'],
                proc['status'],
                str(proc['num_threads']),
                f"{proc['memory_usage']} MB",
                proc['allocated_resources'],
                proc['requested_resources']
            ]):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if row_color:
                    item.setBackground(row_color)
                self.process_table.setItem(row, col, item)
        
        # Auto update graph after fetch
        self.manual_graph_update()
        
    def manual_graph_update(self):
        self.ax_threads.clear()
        
        # Get processes for graph
        process_count = self.process_table.rowCount()
        if process_count == 0:
            return
            
        # Get top 10 processes by memory usage
        start_index = max(0, process_count - 10)
        
        # Extract process names and memory usage
        process_names = []
        memory_usages = []
        
        for i in range(start_index, process_count):
            try:
                name = self.process_table.item(i, 2).text()
                # Truncate long process names
                if len(name) > 15:
                    name = name[:12] + "..."
                process_names.append(name)
                
                # Extract memory usage from the memory column
                memory_str = self.process_table.item(i, 5).text().replace(" MB", "")
                memory_usages.append(float(memory_str))
            except Exception as e:
                print(f"Error extracting data for graph: {e}")
        
        # Horizontal bar chart with custom styling
        bars = self.ax_threads.barh(process_names, memory_usages, color=self.accent_color)
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            self.ax_threads.text(
                width + 1, 
                bar.get_y() + bar.get_height()/2,
                f'{width:.1f} MB', 
                va='center', 
                color='white', 
                fontsize=8
            )
        
        self.ax_threads.set_xlabel("Memory Usage (MB)")
        self.ax_threads.set_title("Top Processes by Memory Usage")
        self.ax_threads.spines['top'].set_visible(False)
        self.ax_threads.spines['right'].set_visible(False)
        self.ax_threads.spines['bottom'].set_color('#555555')
        self.ax_threads.spines['left'].set_color('#555555')
        self.ax_threads.tick_params(colors='white')
        
        # Ensure x-axis starts from 0
        max_memory = max(memory_usages) if memory_usages else 100
        self.ax_threads.set_xlim(0, max_memory * 1.1)
        
        # Add grid lines
        self.ax_threads.grid(axis='x', linestyle='--', alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def detect_deadlock(self):
        try:
            # Ensure we have process data before proceeding
            if self.process_table.rowCount() == 0:
                self.deadlock_response.setText("⚠️ Please fetch processes first.")
                return

            # Change button state
            self.detect_deadlock_button.setEnabled(False)
            self.detect_deadlock_button.setText("🔍 Analyzing...")
            self.deadlock_response.setText("🤖 AI is analyzing processes for potential deadlocks...\n\nThis may take a moment.")
            QApplication.processEvents()

            # More robust process data extraction
            process_data = []
            for i in range(self.process_table.rowCount()):
                try:
                    proc_dict = {
                        'pid': self.process_table.item(i, 1).text(),
                        'name': self.process_table.item(i, 2).text(),
                        'status': self.process_table.item(i, 3).text(),
                        'num_threads': self.process_table.item(i, 4).text(),
                        'memory_usage': self.process_table.item(i, 5).text().replace(" MB", ""),
                        'cpu_usage': self.process_table.item(i, 7).text().split("CPU: ")[1].split("%")[0] if "CPU:" in self.process_table.item(i, 7).text() else "0",
                        'allocated_resources': self.process_table.item(i, 6).text(),
                        'requested_resources': self.process_table.item(i, 7).text()
                    }
                    process_data.append(proc_dict)
                except Exception as e:
                    print(f"Error processing row {i}: {e}")

            # Check if we have valid process data
            if not process_data:
                self.deadlock_response.setText("⚠️ No valid process data to analyze.")
                self.detect_deadlock_button.setEnabled(True)
                self.detect_deadlock_button.setText("🚨 Detect Deadlocks")
                return

            self.deadlock_thread = DeadlockDetectionThread(process_data)
            self.deadlock_thread.result_signal.connect(self.update_deadlock_response)
            self.deadlock_thread.start()

        except Exception as e:
            self.deadlock_response.setText(f"❌ Error in deadlock detection: {str(e)}")
            self.detect_deadlock_button.setEnabled(True)
            self.detect_deadlock_button.setText("🚨 Detect Deadlocks")
    
    def update_deadlock_response(self, text):
        # Format the response text
        formatted_text = "## AI Deadlock Analysis Results\n\n" + text
        self.deadlock_response.setText(formatted_text)
        
        # Reset button state
        self.detect_deadlock_button.setEnabled(True)
        self.detect_deadlock_button.setText("🚨 Detect Deadlocks")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better dark theme support
    gui = DeadlockDetectorGUI1()
    gui.show()
    sys.exit(app.exec())
