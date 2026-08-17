from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout


class LogPanel(QWidget):
    """UI Panel for displaying live system logs and console outputs."""

    def __init__(self, config_manager, logger):
        super().__init__()
        self.config = config_manager
        self.logger = logger
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title Label
        title = QLabel(self.config.get("tab_log", "Log Console"))
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Text Console Output Area
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #0d1117; color: #c9d1d9; font-family: monospace;")
        layout.addWidget(self.console)

        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.export_btn = QPushButton(self.config.get("btn_export_log", "Export Log"))
        self.clear_btn = QPushButton(self.config.get("btn_clear_log", "Clear Log"))
        self.clear_btn.clicked.connect(self.console.clear)
        
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

    def connect_signals(self):
        # Connect logger signal to console output slot
        self.logger.signal.log_emitted.connect(self.append_log)

    def append_log(self, level, message):
        color_map = {
            "DEBUG": "#8b949e",
            "INFO": "#58a6ff",
            "WARNING": "#d29922",
            "ERROR": "#f85149",
            "CRITICAL": "#ff7b72"
        }
        color = color_map.get(level, "#c9d1d9")
        formatted_msg = f"<span style='color: {color};'>[{level}] {message}</span>"
        self.console.append(formatted_msg)
