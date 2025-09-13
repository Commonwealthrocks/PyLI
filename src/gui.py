## gui.py
## last updated: 11/9/2025 <d/m/y>
## p-y-l-i
from importzz import *
from core import BatchProcessorThread
from stylez import STYLE_SHEET
from outs import ProgressDialog, CustomDialog, ErrorExportDialog, DebugConsole
from sfx import SoundManager
from sm import isca

def is_admin():
    try:
        if sys.platform == "win32":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

class QtStream(QObject):
    text_written = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._buffer = []
        self._target_connected = False

    def write(self, text):
        if not self._target_connected:
            self._buffer.append(text)
        else:
            self.text_written.emit(str(text))

    def flush(self):
        pass

    def connect_target(self, target_slot):
        self.text_written.connect(target_slot)
        self._target_connected = True
        if self._buffer:
            buffered_text = "".join(self._buffer)
            self.text_written.emit(buffered_text)
            self._buffer = []

class PyLI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyLI")
        self.setGeometry(100, 100, 500, 380)
        self.setFixedSize(500, 380)
        self.setStyleSheet(STYLE_SHEET)
        self.setAcceptDrops(True)
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
        self.files_to_process = []
        self.custom_ext = "dat"
        self.output_dir = ""
        self.new_name_type = "keep"
        self.mute_sfx = False
        self.chunk_size_mb = 3
        self.kdf_iterations = 1000000
        self.secure_clear = False
        self.add_recovery_data = False
        self.compression_level = "none"
        self.archive_mode = False
        self.batch_processor = None
        self.progress_dialog = None
        self.config_path = self.get_config_path()
        self.load_settings()
        self.validate_output_dir()
        self.sound_manager = SoundManager()
        self.sound_manager.list_available_sounds()
        self.sound_manager.load_sound("success.wav")
        self.sound_manager.load_sound("error.wav")
        self.sound_manager.load_sound("info.wav")
        self.is_admin = is_admin()
        self.debug_console = None
        self.init_debug_console()
        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_main_tab(), "Main")
        self.tab_widget.addTab(self.create_settings_tab(), "Settings")
        self.tab_widget.addTab(self.create_about_tab(), "About")
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
        if self.is_admin:
            dialog = CustomDialog("Warning", "You are running PyLI with Administrator privileges, due to this some feature's like drag n' drop for Windows will be disabled.\n\nWhy? Yeah I got no fucking clue too.", self)
            dialog.exec()

    def init_debug_console(self):
        if self.is_admin:
            VER = "0.8a"
            self.debug_console = DebugConsole(parent=self)
            print("--- PyLI debug console Initialized (Administrator) ---")
            print(f"--- Version: {VER} ---")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_0 and event.modifiers() == Qt.AltModifier:
            if self.is_admin and self.debug_console:
                if self.debug_console.isVisible():
                    self.debug_console.hide()
                else:
                    self.debug_console.show()
        else:
            super().keyPressEvent(event)

    def get_config_path(self):
        if sys.platform == "win32":
            return os.path.join(os.environ["APPDATA"], "PyLI", "config.json")
        else:
            return os.path.join(os.path.expanduser("~"), ".pyli", "config.json")

    def validate_output_dir(self):
        if self.output_dir and not os.path.exists(self.output_dir):
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~")
            self.output_dir = desktop_path
            self.save_settings()
            dialog = CustomDialog("Output directory fix", f"Your output directory was invalid and has been changed to:\n{desktop_path}\n\nThank me later :3", self)
            dialog.exec()

    def load_settings(self):
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                self.custom_ext = config.get("custom_ext", "dat")
                self.output_dir = config.get("output_dir", "")
                self.new_name_type = config.get("new_name_type", "keep")
                self.mute_sfx = config.get("mute_sfx", False)
                self.chunk_size_mb = config.get("chunk_size_mb", 3)
                self.kdf_iterations = config.get("kdf_iterations", 1000000)
                self.secure_clear = config.get("secure_clear", False)
                self.add_recovery_data = config.get("add_recovery_data", False)
                self.compression_level = config.get("compression_level", "none")
                self.archive_mode = config.get("archive_mode", False)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        except Exception as e:
            self.sound_manager.play_sound("error.wav")
            dialog = CustomDialog("Oi blyat...", f"Failed to load settings: {e}", self)
            dialog.exec()

    def save_settings(self):
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config = {
            "custom_ext": self.custom_ext,
            "output_dir": self.output_dir,
            "new_name_type": self.new_name_type,
            "mute_sfx": self.mute_sfx,
            "chunk_size_mb": self.chunk_size_mb,
            "kdf_iterations": self.kdf_iterations,
            "secure_clear": self.secure_clear,
            "add_recovery_data": self.add_recovery_data,
            "compression_level": self.compression_level,
            "archive_mode": self.archive_mode
        }
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

    def create_main_tab(self):
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        input_group = QGroupBox("Select file(s) or folder (drag n' drop)")
        input_layout = QVBoxLayout()
        self.input_path_field = QLineEdit()
        self.input_path_field.setReadOnly(True)
        self.input_path_field.setPlaceholderText("Drag and drop file(s) or folder here...")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.select_files)
        input_layout.addWidget(self.input_path_field)
        input_layout.addWidget(browse_button)
        input_group.setLayout(input_layout)
        password_group = QGroupBox("Encryption / decryption password")
        password_layout = QVBoxLayout()
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setPlaceholderText("Enter password")
        password_layout.addWidget(self.password_field)
        password_group.setLayout(password_layout)
        button_layout = QHBoxLayout()
        self.encrypt_button = QPushButton("Encrypt")
        self.encrypt_button.clicked.connect(lambda: self.start_operation("encrypt"))
        self.decrypt_button = QPushButton("Decrypt")
        self.decrypt_button.clicked.connect(lambda: self.start_operation("decrypt"))
        button_layout.addWidget(self.encrypt_button)
        button_layout.addWidget(self.decrypt_button)
        self.status_label = QLabel("[INFO] Ready.")
        self.status_label.setStyleSheet("color: #7FFF00;")
        main_layout.addWidget(input_group)
        main_layout.addWidget(password_group)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()
        return main_tab

    def create_settings_general_tab(self):
        general_tab = QWidget()
        layout = QVBoxLayout(general_tab)
        output_group = QGroupBox("Output settings")
        output_layout = QFormLayout()
        self.custom_ext_field = QLineEdit(self.custom_ext)
        output_layout.addRow("Custom extension:", self.custom_ext_field)  
        output_dir_layout = QHBoxLayout()
        self.output_dir_field = QLineEdit(self.output_dir)
        self.output_dir_field.setReadOnly(True)
        self.output_dir_browse_button = QPushButton("Browse")
        self.output_dir_browse_button.clicked.connect(self.select_output_dir)
        output_dir_layout.addWidget(self.output_dir_field)
        output_dir_layout.addWidget(self.output_dir_browse_button)
        output_layout.addRow("Output directory:", output_dir_layout)  
        self.new_name_type_combo = QComboBox()
        self.new_name_type_combo.addItems(["keep", "hash", "base64"])
        self.new_name_type_combo.setCurrentText(self.new_name_type)
        output_layout.addRow("New name type:", self.new_name_type_combo)
        self.archive_mode_checkbox = QCheckBox()
        self.archive_mode_checkbox.setChecked(self.archive_mode)
        self.archive_mode_checkbox.setToolTip("When multiple files are selected for encryption, combine them into a single archive file first.\nDecryption will extract all files to a folder.")
        output_layout.addRow("Archive mode:", self.archive_mode_checkbox)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        layout.addStretch()
        return general_tab

    def create_settings_audio_tab(self):
        audio_tab = QWidget()
        layout = QVBoxLayout(audio_tab)
        audio_group = QGroupBox("Audio settings")
        audio_layout = QFormLayout()
        self.mute_sfx_checkbox = QCheckBox()
        self.mute_sfx_checkbox.setChecked(self.mute_sfx)
        audio_layout.addRow("Mute sfx:", self.mute_sfx_checkbox)
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        layout.addStretch()
        return audio_tab

    def handle_warning_checkbox(self, state, checkbox, title, message):
        if state:
            self.play_warning_sound()
            dialog = CustomDialog(title, message, self)
            if dialog.exec() != QDialog.Accepted:
                checkbox.setChecked(False)

    def check_ultrakill_warning(self, text):
        if "ULTRAKILL" in text:
            self.play_warning_sound()
            if text == "[L] ULTRAKILL (???)":
                message = "You have selected the legacy LZMA 'ULTRAKILL' compression.\n\nThis will take an extremely long time and might make CPU's cry, no promises!!"
            else:
                message = "You have selected 'ULTRAKILL' compression level.\n\nThis will be quite slow and CPU intensive."
            dialog = CustomDialog("Warning (like fr this time)", message, self)
            dialog.exec()

    def create_settings_advanced_tab(self):
        advanced_tab = QWidget()
        main_layout = QVBoxLayout(advanced_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; }
            QGroupBox { margin-bottom: 10px; }
        """)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        compression_group = QGroupBox("Compression")
        compression_layout = QFormLayout()
        self.compression_combo = QComboBox()
        self.compression_combo.addItems(["None", "Normal (fast)", "Best (slow-er)", "ULTRAKILL (probably slow)", "[L] ULTRAKILL (???)"])
        compression_mapping = {"None": "none", "Normal (fast)": "normal", "Best (slow-er)": "best", "ULTRAKILL (probably slow)": "ultrakill", "[L] ULTRAKILL (???)": "[L] ultrakill"}
        current_text = [k for k, v in compression_mapping.items() if v == self.compression_level][0]
        self.compression_combo.setCurrentText(current_text)
        self.compression_combo.setToolTip("Selects the compression algorithm to use before encryption.\n'None' is fastest. Higher levels give better compression but are slower.\nCompression is automatically skipped for already compressed file types (e.g., jpg, mp4 and so on...).")
        compression_layout.addRow("Compression Level:", self.compression_combo)
        compression_group.setLayout(compression_layout)
        security_group = QGroupBox("Security/Data integrity")
        security_layout = QFormLayout()
        self.secure_clear_checkbox = QCheckBox()
        self.secure_clear_checkbox.setChecked(self.secure_clear)
        if not isca():
            self.secure_clear_checkbox.setEnabled(False)
            self.secure_clear_checkbox.setToolTip("Disabled: eh, C library not found... a shame for you.")
        else:
            self.secure_clear_checkbox.stateChanged.connect(lambda state: self.handle_warning_checkbox(state, self.secure_clear_checkbox, "Warning",
                "This enables a feature to overwrite the password in memory after use.\n\nThis is an experimental security measure and relies on a compiled C library, aka shit MIGHT go wrong!!"))
        security_layout.addRow("Securely clear password from memory:", self.secure_clear_checkbox)
        self.recovery_checkbox = QCheckBox()
        self.recovery_checkbox.setChecked(self.add_recovery_data)
        self.recovery_checkbox.stateChanged.connect(lambda state: self.handle_warning_checkbox(state, self.recovery_checkbox, "Warning",
            "This adds Reed Solomon recovery data to each chunk.\n\nThis can help repair files from minor corruption (bit rot) but will increase file size and processing time. It does not protect against malicious tampering fuck face."))
        security_layout.addRow("Add partial data recovery info:", self.recovery_checkbox)
        security_group.setLayout(security_layout)
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout()
        self.chunk_size_spinbox = QSpinBox()
        self.chunk_size_spinbox.setRange(1, 128)
        self.chunk_size_spinbox.setValue(self.chunk_size_mb)
        self.chunk_size_spinbox.setSuffix(" MB")
        performance_layout.addRow("Chunk size:", self.chunk_size_spinbox)
        self.kdf_iterations_spinbox = QSpinBox()
        self.kdf_iterations_spinbox.setRange(100000, 5000000)
        self.kdf_iterations_spinbox.setSingleStep(100000)
        self.kdf_iterations_spinbox.setValue(self.kdf_iterations)
        self.kdf_iterations_spinbox.setGroupSeparatorShown(True)
        performance_layout.addRow("KDF iterations:", self.kdf_iterations_spinbox)
        performance_group.setLayout(performance_layout)
        layout.addWidget(compression_group)
        layout.addWidget(security_group)
        layout.addWidget(performance_group)
        layout.addStretch()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        return advanced_tab

    def create_settings_tab(self):
        settings_tab = QWidget()
        main_settings_layout = QVBoxLayout(settings_tab)
        sub_tab_widget = QTabWidget()
        general_tab = self.create_settings_general_tab()
        audio_tab = self.create_settings_audio_tab()
        advanced_tab = self.create_settings_advanced_tab()
        sub_tab_widget.addTab(general_tab, "General")
        sub_tab_widget.addTab(audio_tab, "Audio")
        sub_tab_widget.addTab(advanced_tab, "Advanced")
        save_button = QPushButton("Save settings")
        save_button.clicked.connect(self.update_settings)
        main_settings_layout.addWidget(sub_tab_widget)
        main_settings_layout.addWidget(save_button)
        return settings_tab

    def create_about_tab(self):
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        self.about_tab_widget = QTabWidget()
        disclaimer_tab = self.create_disclaimer_tab()
        self.about_tab_widget.addTab(disclaimer_tab, "Legal stuff")
        info_tab = self.create_info_tab()
        self.about_tab_widget.addTab(info_tab, "Nerd info")
        changelog_tab = self.create_log_tab()
        self.about_tab_widget.addTab(changelog_tab, "Changelogs")
        about_layout.addWidget(self.about_tab_widget)
        return about_tab

    def create_disclaimer_tab(self):
        disclaimer_widget = QWidget()
        disclaimer_layout = QVBoxLayout(disclaimer_widget)
        info_label = QLabel("PyLI")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        subtitle_label = QLabel("WinRAR Is Probably Enough But Use This For Your Needs™")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 12pt; font-style: italic; margin-bottom: 20px;")
        disclaimer_text = self.load_disclaimer()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        disclaimer_label = QLabel(disclaimer_text)
        disclaimer_label.setWordWrap(True)
        disclaimer_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        disclaimer_label.setStyleSheet("font-size: 9pt; padding: 15px; border: 1px solid #666; background-color: #2A2A2A; border-radius: 5px; line-height: 1.4;")
        scroll_area.setWidget(disclaimer_label)
        disclaimer_layout.addWidget(info_label)
        disclaimer_layout.addWidget(subtitle_label)
        disclaimer_layout.addWidget(scroll_area)
        return disclaimer_widget

    def create_info_tab(self):
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        title_label = QLabel("Technical Information")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 20px;")
        info_text = self.load_info()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_label.setStyleSheet("font-size: 9pt; padding: 15px; border: 1px solid #666; background-color: #2A2A2A; border-radius: 5px; line-height: 1.4; font-family: 'Consolas', 'Monaco', monospace;")
        scroll_area.setWidget(info_label)
        info_layout.addWidget(title_label)
        info_layout.addWidget(scroll_area)
        return info_widget

    def create_log_tab(self):
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        title_label = QLabel("Changelogs")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 20px;")
        log_text = self.load_log()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        log_label = QLabel(log_text)
        log_label.setWordWrap(True)
        log_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        log_label.setStyleSheet("font-size: 9pt; padding: 15px; border: 1px solid #666; background-color: #2A2A2A; border-radius: 5px; line-height: 1.4; font-family: 'Consolas', 'Monaco', monospace;")
        scroll_area.setWidget(log_label)
        log_layout.addWidget(title_label)
        log_layout.addWidget(scroll_area)
        return log_widget

    def load_disclaimer(self):
        try:
            if getattr(sys, "frozen", False): disclaimer_path = os.path.join(sys._MEIPASS, "txts", "disclaimer.txt")
            else: disclaimer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "txts", "disclaimer.txt")
            with open(disclaimer_path, "r", encoding="utf-8") as f: return f.read().strip()
        except Exception: return "Disclaimer file not found."

    def load_info(self):
        try:
            if getattr(sys, "frozen", False): disclaimer_path = os.path.join(sys._MEIPASS, "txts", "info.txt")
            else: disclaimer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "txts", "info.txt")
            with open(disclaimer_path, "r", encoding="utf-8") as f: return f.read().strip()
        except Exception: return "Info file not found."

    def load_log(self):
        try:
            if getattr(sys, "frozen", False): disclaimer_path = os.path.join(sys._MEIPASS, "txts", "changelog.txt")
            else: disclaimer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "txts", "changelog.txt")
            with open(disclaimer_path, "r", encoding="utf-8") as f: return f.read().strip()
        except Exception: return "Changelogs file not found."

    def update_settings(self):
        compression_mapping = {"None": "none", "Normal (fast)": "normal", "Best (slow-er)": "best", "ULTRAKILL (probably slow)": "ultrakill", "[L] ULTRAKILL (???)": "[L] ultrakill"}
        self.compression_level = compression_mapping[self.compression_combo.currentText()]
        self.custom_ext = self.custom_ext_field.text()
        self.output_dir = self.output_dir_field.text()
        self.new_name_type = self.new_name_type_combo.currentText()
        self.mute_sfx = self.mute_sfx_checkbox.isChecked()
        self.chunk_size_mb = self.chunk_size_spinbox.value()
        self.kdf_iterations = self.kdf_iterations_spinbox.value()
        self.secure_clear = self.secure_clear_checkbox.isChecked()
        self.add_recovery_data = self.recovery_checkbox.isChecked()
        self.archive_mode = self.archive_mode_checkbox.isChecked()
        if self.output_dir and not os.path.exists(self.output_dir):
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop_path): desktop_path = os.path.expanduser("~")
            self.output_dir = desktop_path
            self.output_dir_field.setText(self.output_dir)
            self.play_warning_sound()
            dialog = CustomDialog("Invalid Path", f"Output directory was invalid and changed to:\n{desktop_path}", self)
            dialog.exec()
        if not self.mute_sfx: self.sound_manager.play_sound("success.wav")
        dialog = CustomDialog("Success", "Settings have been saved to 'config.json'", self)
        dialog.exec()
        self.save_settings()
        self.status_label.setText("[INFO] Settings saved (hopefully)")

    def select_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec():
            self.files_to_process = file_dialog.selectedFiles()
            if len(self.files_to_process) == 1: self.input_path_field.setText(self.files_to_process[0])
            else: self.input_path_field.setText(f"{len(self.files_to_process)} files selected.")
            self.status_label.setText("[INFO] Files ready to process.")

    def select_output_dir(self):
        dir_dialog = QFileDialog()
        dir_dialog.setFileMode(QFileDialog.Directory)
        if dir_dialog.exec():
            selected_dir = dir_dialog.selectedFiles()[0]
            if os.path.exists(selected_dir):
                self.output_dir = selected_dir
                self.output_dir_field.setText(self.output_dir)
            else:
                dialog = CustomDialog("Invalid directory", "Selected directory does not exist, somehow...?", self)
                dialog.exec()

    def start_operation(self, operation):
        password = self.password_field.text()
        if not self.files_to_process:
            self.play_warning_sound()
            dialog = CustomDialog("Eh?", "Maybe choose some file(s) first, pal?", self)
            dialog.exec()
            return
        if not password:
            self.play_warning_sound()
            dialog = CustomDialog("Perhaps no?", "No password?! What the flip.", self)
            dialog.exec()
            return 
        self.status_label.setText("[INFO] Starting...")
        self.encrypt_button.setEnabled(False)
        self.decrypt_button.setEnabled(False)    
        self.progress_dialog = ProgressDialog("Processing...", self)
        self.progress_dialog.canceled.connect(self.cancel_operation)
        self.progress_dialog.show()    
        self.batch_processor = BatchProcessorThread(
            operation=operation, file_paths=self.files_to_process, password=password,
            custom_ext=self.custom_ext, output_dir=self.output_dir, new_name_type=self.new_name_type,
            chunk_size=self.chunk_size_mb * 1024 * 1024, kdf_iterations=self.kdf_iterations,
            secure_clear=self.secure_clear, add_recovery_data=self.add_recovery_data,
            compression_level=self.compression_level, archive_mode=self.archive_mode,
            parent=self)
        self.batch_processor.batch_progress_updated.connect(self.progress_dialog.update_batch_progress)
        self.batch_processor.status_message.connect(lambda msg: self.progress_dialog.file_label.setText(msg))
        self.batch_processor.progress_updated.connect(lambda p: self.progress_dialog.file_progress_bar.setValue(int(p)))
        self.batch_processor.finished.connect(self.on_batch_finished)
        self.batch_processor.start()

    def play_warning_sound(self):
        if not self.mute_sfx:
            self.sound_manager.play_sound("info.wav")

    def cancel_operation(self):
        if self.batch_processor and self.batch_processor.isRunning():
            self.batch_processor.cancel()
        if self.progress_dialog: self.progress_dialog.close()
        self.encrypt_button.setEnabled(True)
        self.decrypt_button.setEnabled(True)
        self.play_warning_sound()
        self.status_label.setText("[INFO] Operation canceled.")

    def on_batch_finished(self, errors):
        if self.progress_dialog: self.progress_dialog.close()
        self.encrypt_button.setEnabled(True)
        self.decrypt_button.setEnabled(True)
        if errors:
            if not self.mute_sfx: self.sound_manager.play_sound("error.wav")
            error_message = "Some files failed to process:\n" + "\n".join(errors)
            self.status_label.setText("[ERROR] Some file(s) failed.")
            dialog = ErrorExportDialog("Ahh kaput...", error_message, errors, self)
            dialog.exec()
        else:
            if not self.mute_sfx: self.sound_manager.play_sound("success.wav")
            self.status_label.setText("[INFO] All file(s) processed successfully.")
            dialog = CustomDialog("Success", "All file(s) processed successfully.", self)
            dialog.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = [url.toLocalFile() for url in event.mimeData().urls()]
        self.files_to_process.clear()
        for url in urls:
            if os.path.isdir(url):
                for root, _, files in os.walk(url):
                    for name in files:
                        self.files_to_process.append(os.path.join(root, name))
            else:
                self.files_to_process.append(url)
        if len(self.files_to_process) == 1: self.input_path_field.setText(self.files_to_process[0])
        else: self.input_path_field.setText(f"{len(self.files_to_process)} files selected.")
        self.status_label.setText("[INFO] File(s) ready to process.")
        event.acceptProposedAction()

    def closeEvent(self, event):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.batch_processor and self.batch_processor.isRunning(): self.batch_processor.cancel()
        self.save_settings()
        self.sound_manager.unload()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stream_redirect = QtStream()
    if is_admin():
        sys.stdout = stream_redirect
        sys.stderr = stream_redirect
    window = PyLI()
    if window.debug_console:
        stream_redirect.connect_target(window.debug_console.append_text)   
    window.show()
    sys.exit(app.exec())

## end