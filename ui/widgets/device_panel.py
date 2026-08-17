from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout


class DevicePanel(QWidget):
    """UI Panel for displaying connected device information and status."""

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Status Header Layout
        status_layout = QHBoxLayout()
        self.status_label = QLabel(self.config.get("status_disconnected", "No Device"))
        self.status_label.setStyleSheet("font-weight: bold; color: #ff5555; font-size: 14px;")
        
        self.refresh_btn = QPushButton(self.config.get("btn_refresh", "Refresh"))
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.refresh_btn)
        layout.addLayout(status_layout)

        # Device Details Table
        self.table = QTableWidget(9, 2)
        self.table.setHorizontalHeaderLabels([
            self.config.get("col_name", "Property"),
            self.config.get("col_status", "Value")
        ])
        self.table.horizontalHeader().setStretchLastSection(True)

        # Populate initial empty fields
        properties = [
            self.config.get("device_model", "Model"),
            self.config.get("device_brand", "Brand"),
            self.config.get("device_android", "Android Version"),
            self.config.get("device_serial", "Serial Number"),
            self.config.get("device_battery", "Battery Level"),
            self.config.get("device_storage", "Storage"),
            self.config.get("device_imei", "IMEI"),
            self.config.get("device_root", "Root Status"),
            self.config.get("device_bootloader", "Bootloader")
        ]

        for row, prop in enumerate(properties):
            self.table.setItem(row, 0, QTableWidgetItem(prop))
            self.table.setItem(row, 1, QTableWidgetItem("N/A"))

        layout.addWidget(self.table)
