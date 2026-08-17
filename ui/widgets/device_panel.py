from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from core.device_detector import DeviceDetector


class DevicePanel(QWidget):
    """UI Panel for displaying connected device information and status."""

    def __init__(self, config_manager, logger):
        super().__init__()
        self.config = config_manager
        self.logger = logger
        self.detector = DeviceDetector(
            adb_path=self.config.get_setting("adb_path", "tools/adb.exe"),
            fastboot_path=self.config.get_setting("fastboot_path", "tools/fastboot.exe")
        )
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Status Header Layout
        status_layout = QHBoxLayout()
        self.status_label = QLabel(self.config.get("status_disconnected", "No Device"))
        self.status_label.setStyleSheet("font-weight: bold; color: #ff5555; font-size: 14px;")
        
        self.refresh_btn = QPushButton(self.config.get("btn_refresh", "Refresh"))
        self.refresh_btn.clicked.connect(self.scan_devices)
        
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

        self.properties_keys = [
            ("device_model", "model"),
            ("device_brand", "brand"),
            ("device_android", "android_version"),
            ("device_serial", "serial"),
            ("device_battery", "battery"),
            ("device_storage", "storage_total"),
            ("device_imei", "imei"),
            ("device_root", "rooted"),
            ("device_bootloader", "bootloader_unlocked")
        ]

        for row, (label_key, _) in enumerate(self.properties_keys):
            prop_name = self.config.get(label_key, label_key)
            self.table.setItem(row, 0, QTableWidgetItem(prop_name))
            self.table.setItem(row, 1, QTableWidgetItem("N/A"))

        layout.addWidget(self.table)

    def scan_devices(self):
        self.logger.info("Scanning for connected devices (ADB, Fastboot, USB)...")
        devices = self.detector.detect_all()

        if not devices:
            self.status_label.setText(self.config.get("status_disconnected", "No Device"))
            self.status_label.setStyleSheet("font-weight: bold; color: #ff5555; font-size: 14px;")
            self.logger.warning("No devices detected.")
            self._clear_table()
            return

        # Take the first detected device for display
        dev = devices[0]
        self.status_label.setText(f"{self.config.get('status_connected', 'Device Connected')} ({dev.connection.upper()})")
        self.status_label.setStyleSheet("font-weight: bold; color: #238636; font-size: 14px;")
        self.logger.info(f"Device found: Model={dev.model}, Connection={dev.connection}, Serial={dev.serial}")

        # Update table with device info
        dev_dict = dev.to_dict()
        for row, (_, attr_key) in enumerate(self.properties_keys):
            val = str(dev_dict.get(attr_key, "N/A"))
            if not val or val == "None":
                val = "N/A"
            self.table.setItem(row, 1, QTableWidgetItem(val))

    def _clear_table(self):
        for row in range(len(self.properties_keys)):
            self.table.setItem(row, 1, QTableWidgetItem("N/A"))
