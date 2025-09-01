## outs.py
## last updated: 20/8/2025 <d/m/y>
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
        self.export_button = QPushButton("Export Errors")
        self.export_button.clicked.connect(self.export_errors)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)     
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)      
        self.setLayout(layout)
    
    def export_errors(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Errors", "errors.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write("\n".join(self.errors))
            dialog = CustomDialog("Export Successful", f"Errors exported to:\n{file_path}", self)
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

## end