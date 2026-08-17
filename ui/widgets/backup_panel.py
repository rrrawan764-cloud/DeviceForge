from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QHBoxLayout


class BackupPanel(QWidget):
    """UI Panel for managing full or selective device backups and restorations."""

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title Label
        title = QLabel(self.config.get("tab_backup", "Backup & Restore"))
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Backup Options / Checkboxes
        self.chk_apps = QCheckBox("Backup Applications & Data (.apk + data)")
        self.chk_apps.setChecked(True)
        layout.addWidget(self.chk_apps)

        self.chk_storage = QCheckBox("Backup Internal Storage (Photos, Media)")
        layout.addWidget(self.chk_storage)

        self.chk_system = QCheckBox("Backup System Settings & Accounts")
        self.chk_system.setChecked(True)
        layout.addWidget(self.chk_system)

        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        
        self.backup_btn = QPushButton(self.config.get("btn_backup", "Create Backup"))
        self.backup_btn.setStyleSheet("background-color: #1f6feb; color: white; font-weight: bold; padding: 8px;")
        
        self.restore_btn = QPushButton(self.config.get("btn_restore", "Restore Backup"))
        self.restore_btn.setStyleSheet("background-color: #8957e5; color: white; font-weight: bold; padding: 8px;")
        
        btn_layout.addWidget(self.backup_btn)
        btn_layout.addWidget(self.restore_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
