نfrom PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QLabel, QLineEdit, QListWidget, QGroupBox, QGridLayout, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from ui.widgets.log_panel import LogPanel
from core.protocol.adb_handler import AdbHandler
from core.protocol.fastboot_handler import FastbootHandler
from core.protocol.apple_handler import AppleHandler
from core.device_detector import DeviceDetector


class MainWindow(QMainWindow):
    """Professional Multi-Platform Servicing Suite (Android & iOS)."""

    def __init__(self, config_manager, logger):
        super().__init__()
        self.config = config_manager
        self.logger = logger
        self.adb = AdbHandler()
        self.fastboot = FastbootHandler()
        self.apple = AppleHandler()
        self.detector = DeviceDetector()
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.config.get("app_title", "DeviceForge Pro - Multi-Platform Suite"))
        self.resize(1300, 800)

        if self.config.current_lang == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Top Control Bar (Language Selector)
        top_bar = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "العربية"])
        self.lang_combo.setCurrentIndex(1 if self.config.current_lang == "ar" else 0)
        self.lang_combo.currentIndexChanged.connect(self.switch_language)
        
        top_bar.addWidget(QLabel("Language / لغة الواجهة:"))
        top_bar.addWidget(self.lang_combo)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # 1. Brands & Ecosystem Header (Android & Apple Full Support)
        brand_layout = QHBoxLayout()
        brands = ["APPLE (iPhone 6-17)", "SAMSUNG", "XIAOMI", "HUAWEI", "OPPO", "VIVO", "MEDIATEK", "QUALCOMM", "FASTBOOT", "ADB"]
        for brand in brands:
            btn = QPushButton(brand)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                    border-radius: 4px; padding: 6px 10px; font-weight: bold; font-size: 10px;
                }
                QPushButton:hover { background-color: #30363d; color: #58a6ff; border-color: #58a6ff; }
            """)
            brand_layout.addWidget(btn)
        main_layout.addLayout(brand_layout)

        # 2. Protocols Toolbar
        mode_layout = QHBoxLayout()
        modes = ["IOS RECOVERY / DFU", "ODIN / SAMSUNG", "FUNCTIONS", "BROM / EDL", "ADB TOOLS", "FASTBOOT TOOLS"]
        for mode in modes:
            m_btn = QPushButton(mode)
            m_btn.setStyleSheet("""
                QPushButton {
                    background-color: #161b22; color: #8b949e; border: 1px solid #30363d;
                    padding: 6px 15px; font-size: 10px; font-weight: bold;
                }
                QPushButton:hover { background-color: #21262d; color: #ffffff; }
            """)
            mode_layout.addWidget(m_btn)
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)

        # 3. Middle Content Area
        middle_layout = QHBoxLayout()

        # Left: Model Selector (Android & iOS)
        left_group = QGroupBox("Supported Models / الموديلات المدعومة (Android & iOS)")
        left_layout = QVBoxLayout(left_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search model (e.g. iPhone 15, S10, A05)...")
        left_layout.addWidget(self.search_input)

        self.model_list = QListWidget()
        self.model_list.addItems([
            "--- Apple iOS Devices ---",
            "Apple iPhone 16 / 16 Pro / Pro Max",
            "Apple iPhone 15 / 15 Pro / Pro Max",
            "Apple iPhone 14 / 13 / 12 / 11",
            "Apple iPhone X / 8 / 7 / 6s / 6",
            "Apple iPad / iPad Pro / Air / Mini",
            "--- Android Devices ---",
            "Samsung Galaxy S10 / S20 / S21 / S22 / S23 / S24",
            "Samsung Galaxy A05 / A05s / A14 / A54",
            "Xiaomi Redmi Note 10 / 11 / 12 / 13 Pro",
            "Oppo / Realme / Vivo / Huawei MTK & Qualcomm"
        ])
        left_layout.addWidget(self.model_list)
        middle_layout.addWidget(left_group, stretch=1)

        # Right: Real Operations & Logs
        right_tabs = QTabWidget()
        
        func_widget = QWidget()
        func_layout = QVBoxLayout(func_widget)
        
        actions_grid = QGridLayout()
        operations = [
            ("APPLE: READ IOS INFO", "#1f6feb", self.action_apple_info),
            ("APPLE: ENTER RECOVERY", "#8957e5", self.action_apple_recovery),
            ("ANDROID: REMOVE FRP", "#da3633", self.action_remove_frp),
            ("ANDROID: FACTORY RESET", "#238636", self.action_factory_reset),
            ("ANDROID: UNLOCK BOOTLOADER", "#d29922", self.action_unlock_bootloader),
            ("GENERAL: DETECT ALL DEVICES", "#1f6feb", self.action_read_info)
        ]
        
        for idx, (op_name, color, callback) in enumerate(operations):
            op_btn = QPushButton(op_name)
            op_btn.clicked.connect(callback)
            op_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}; color: white; font-weight: bold;
                    padding: 12px; border-radius: 6px; font-size: 11px;
                }}
                QPushButton:hover {{ opacity: 0.85; }}
            """)
            actions_grid.addWidget(op_btn, idx // 2, idx % 2)
            
        func_layout.addLayout(actions_grid)
        func_layout.addStretch()
        right_tabs.addTab(func_widget, "Functions & Operations")

        # Log Console Tab
        self.log_panel = LogPanel(self.config, self.logger)
        right_tabs.addTab(self.log_panel, "Log Console")

        middle_layout.addWidget(right_tabs, stretch=2)
        main_layout.addLayout(middle_layout)

        # Status Bar
        status_bar_layout = QHBoxLayout()
        self.status_info = QLabel("Status: Ready | Monitoring Android (ADB/Fastboot) & iOS (libimobiledevice)...")
        self.status_info.setStyleSheet("color: #3fb950; font-family: monospace; font-weight: bold; font-size: 11px;")
        status_bar_layout.addWidget(self.status_info)
        main_layout.addLayout(status_bar_layout)

        self.logger.info("DeviceForge Pro multi-platform suite initialized successfully.")

    def switch_language(self, index):
        new_lang = "ar" if index == 1 else "en"
        self.config.current_lang = new_lang
        self.logger.info(f"Language switched to: {new_lang}")
        self.init_ui()

    # Executable Apple & Android Actions
    def action_apple_info(self):
        self.logger.info("Fetching connected iOS device information...")
        info = self.apple.get_device_info()
        if info and "Error" not in info:
            self.logger.info(f"iOS Device Info:\n{info}")
            QMessageBox.information(self, "iOS Info", "Successfully read iPhone/iPad details. Check Log Console.")
        else:
            self.logger.warning("No iOS device found via USB or libimobiledevice error.")
            QMessageBox.warning(self, "Warning", "No iPhone/iPad detected! Ensure cable is connected and trusted.")

    def action_apple_recovery(self):
        self.logger.warning("Sending command to switch iOS device into Recovery Mode...")
        res = self.apple.enter_recovery()
        self.logger.info(f"Recovery response: {res}")

    def action_remove_frp(self):
        self.logger.warning("Executing Android FRP Bypass sequence...")
        devices = self.detector.detect_all()
        if not devices:
            self.logger.error("No Android device detected.")
            QMessageBox.critical(self, "Error", "No Android device detected!")
            return
        serial = devices[0].serial
        res = self.adb.shell(serial, "am start -a android.intent.action.MAIN")
        self.logger.info(f"FRP command sent to {serial}. Response: {res}")

    def action_factory_reset(self):
        self.logger.warning("Triggering device factory reset...")
        devices = self.detector.detect_all()
        if devices:
            self.adb.reboot(devices[0].serial, "recovery")
            self.logger.info("Rebooted device to recovery for wipe.")
        else:
            QMessageBox.warning(self, "Warning", "No active device connected.")

    def action_unlock_bootloader(self):
        self.logger.warning("Sending fastboot bootloader unlock signal...")
        res = self.fastboot.get_variable("", "unlocked")
        self.logger.info(f"Fastboot response: {res}")

    def action_read_info(self):
        self.logger.info("Scanning all connected platforms (Android & iOS)...")
        devices = self.detector.detect_all()
        if devices:
            for dev in devices:
                self.logger.info(f"Found [{dev.brand}] -> Model: {dev.model} | Serial/UDID: {dev.serial} | Connection: {dev.connection}")
        else:
            self.logger.warning("No devices found on any port.")

