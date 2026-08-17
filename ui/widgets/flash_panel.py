from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QFileDialog, QLineEdit


class FlashPanel(QWidget):
    """UI Panel for managing firmware flashing and partition writing."""

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title Label
        title = QLabel(self.config.get("tab_flash", "Flash & Firmware"))
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Firmware Selection Layout
        file_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select firmware package or image (.zip, .tar, .img)...")
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.path_input)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # Partition / Target Selection
        self.partition_combo = QComboBox()
        self.partition_combo.addItems(["Entire Firmware (Auto)", "boot.img", "recovery.img", "system.img", "vendor.img"])
        layout.addWidget(self.partition_combo)

        # Flash Action Button
        self.flash_btn = QPushButton(self.config.get("btn_flash", "Start Flash"))
        self.flash_btn.setStyleSheet("background-color: #238636; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(self.flash_btn)
        
        layout.addStretch()

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Firmware File", "", "Image Files (*.img *.zip *.tar);;All Files (*.*)")
        if file_name:
            self.path_input.setText(file_name)
