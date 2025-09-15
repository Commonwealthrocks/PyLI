## outs.py
## last updated: 11/09/2025 <d/m/y>
## p-y-l-i
from importzz import *

class CustomDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("QTextEdit { background-color: #3C3C3C; color: #E0E0E0; border: 1px solid #5A5A5A; }")
        if hasattr(Qt, "AA_DontCreateNativeWidgetSiblings"):
            QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                hwnd = int(self.winId())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = wintypes.DWORD(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            except:
                pass
        layout = QVBoxLayout(self)
        self.message_label = QLabel(title)
        self.message_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self.message_label)
        self.message_text = QTextEdit()
        self.message_text.setPlainText(message)
        self.message_text.setReadOnly(True)
        layout.addWidget(self.message_text)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

class ErrorExportDialog(QDialog):
    def __init__(self, title, message, errors, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(500, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("QTextEdit { background-color: #3C3C3C; color: #E0E0E0; border: 1px solid #5A5A5A; }")
        if hasattr(Qt, "AA_DontCreateNativeWidgetSiblings"):
            QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                hwnd = int(self.winId())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = wintypes.DWORD(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            except:
                pass
        self.errors = errors
        layout = QVBoxLayout(self)
        self.message_label = QLabel(title)
        self.message_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self.message_label)
        self.message_text = QTextEdit()
        self.message_text.setPlainText(message)
        self.message_text.setReadOnly(True)
        layout.addWidget(self.message_text)
        button_layout = QHBoxLayout()
        self.export_button = QPushButton("Export errors")
        self.export_button.clicked.connect(self.export_errors)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)     
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)      
        self.setLayout(layout)
    
    def export_errors(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export errors", "this_software_fucking_sucks.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as f:
                f.write("\n".join(self.errors))
            dialog = CustomDialog("Export successful", f"Errors exported to:\n{file_path}", self)
            dialog.exec()


class ProgressDialog(QDialog):
    canceled = pyqtSignal()
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 150)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout(self)       
        self.batch_label = QLabel("Total Progress: (0/0)")
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setRange(0, 100)
        self.batch_progress_bar.setValue(0)
        self.file_label = QLabel("Current File:")
        self.file_progress_bar = QProgressBar()
        self.file_progress_bar.setRange(0, 100)
        self.file_progress_bar.setValue(0)        
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        if hasattr(Qt, "AA_DontCreateNativeWidgetSiblings"):
            QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                hwnd = int(self.winId())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = wintypes.DWORD(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            except:
                pass
        self.cancel_button.clicked.connect(self.cancel_operation)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addWidget(self.batch_label)
        layout.addWidget(self.batch_progress_bar)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_progress_bar)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def cancel_operation(self):
        self.canceled.emit()
        self.close()

    def update_batch_progress(self, current, total):
        self.batch_label.setText(f"Total Progress: ({current}/{total})")
        if total > 0:
            self.batch_progress_bar.setValue(int((current / total) * 100))

class DebugConsole(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("DBG")
        self.setGeometry(150, 150, 600, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout(self)
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setStyleSheet("font-family: 'Consolas', 'Monaco', monospace; background-color: #1E1E1E; color: #E0E0E0;")
        if hasattr(Qt, "AA_DontCreateNativeWidgetSiblings"):
            QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes
                hwnd = int(self.winId())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = wintypes.DWORD(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            except:
                pass
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter command (e.g., ?help)...")
        self.input_line.returnPressed.connect(self.process_command)
        layout.addWidget(self.output_view)
        layout.addWidget(self.input_line)
        self.setLayout(layout)

    def append_text(self, text):
        self.output_view.moveCursor(QTextCursor.End)
        self.output_view.insertPlainText(text)
        self.output_view.moveCursor(QTextCursor.End)

    def process_command(self):
        command = self.input_line.text().strip()
        self.input_line.clear()
        self.append_text(f"> {command}\n")
        if not command:
            return
        if not command.startswith("?"):
            self.append_text("Error: Unknown command. Commands must start with '?'.\n")
            return
        parts = command.split()
        cmd = parts[0]
        args = parts[1:]
        if cmd == "?chc_mem":
            self.check_memory_clearing()
        elif cmd == "?test_sfx":
            self.test_sound_effect(args)
        elif cmd == "?help":
            self.append_text("Available commands:\n")
            self.append_text("  ?help             - Shows this help message.\n")
            self.append_text("  ?cls              - Clears the console.\n")
            self.append_text("  ?chc_mem          - Tests the secure memory clearing function.\n")
            self.append_text("  ?test_sfx [sound] - Plays a sound file (e.g., success.wav).\n")
        elif cmd == "?cls":
            self.output_view.clear()
        else:
            self.append_text(f"Error: Unknown command '{cmd}'. Type '?help' for a list of commands.\n")

    def check_memory_clearing(self):
        from sm import clear_buffer, isca
        import ctypes
        self.append_text("--- MCT ---\n")
        if not isca():
            self.append_text("Result: C library for secure memory clearing is NOT loaded.\n")
            self.append_text("Using fallback Python method (less secure).\n")
        else:
            self.append_text("Result: C library for secure memory clearing IS loaded.\n")
        test_string = b"If you can read this, the memory was not cleared."
        buffer = ctypes.create_string_buffer(len(test_string))
        buffer.raw = test_string
        self.append_text(f"Original buffer content: {buffer.raw.decode('utf-8', errors='ignore')}\n")
        clear_buffer(buffer)
        cleared_content = buffer.raw
        self.append_text(f"Buffer content after clearing: {cleared_content}\n")
        if all(b == 0 for b in cleared_content):
            self.append_text("Success: Buffer was successfully zeroed out.\n")
        else:
            self.append_text("Failure: Buffer still contains data (oops)...\n")
        self.append_text("--------------------------\n")

    def test_sound_effect(self, args):
        if not args:
            self.append_text("Error: Missing argument. Usage: ?test_sfx [sound_name]\n")
            return
        sound_name = args[0]
        self.append_text(f"Attempting to play sound: {sound_name}\n")
        if self.parent_app and hasattr(self.parent_app, 'sound_manager'):
            self.parent_app.sound_manager.play_sound(sound_name)
            self.append_text("Play command sent. Check your audio output.\n")
        else:
            self.append_text("Error: Sound manager not found.\n")

    def closeEvent(self, event):
        self.hide()
        event.ignore()

## end