from ui.widgets.device_panel import DevicePanel
from ui.widgets.flash_panel import FlashPanel
from ui.widgets.backup_panel import BackupPanel
from ui.widgets.log_panel import LogPanel


class MainWindow(QMainWindow):
    """Main Application Window housing all tabs, menus, and core managers."""

    def __init__(self, config_manager, logger):
        super().__init__()
        self.config = config_manager
        self.logger = logger
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.config.get("app_title", "DeviceForge Pro"))
        self.resize(1000, 700)

        # Central Widget & Tabs Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        
        # Instantiate Panels (Passing config and logger properly)
        self.device_panel = DevicePanel(self.config, self.logger)
        self.flash_panel = FlashPanel(self.config)
        self.backup_panel = BackupPanel(self.config)
        self.log_panel = LogPanel(self.config, self.logger)

        # Add Tabs
        self.tabs.addTab(self.device_panel, self.config.get("tab_device", "Device Info"))
        self.tabs.addTab(self.flash_panel, self.config.get("tab_flash", "Flash & Firmware"))
        self.tabs.addTab(self.backup_panel, self.config.get("tab_backup", "Backup & Restore"))
        self.tabs.addTab(self.log_panel, self.config.get("tab_log", "Log Console"))

        layout.addWidget(self.tabs)

        # Create Menu Bar
        self.create_menus()
        
        self.logger.info("DeviceForge Pro main window initialized successfully.")

    def create_menus(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu(self.config.get("menu_file", "File"))
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help Menu
        help_menu = menubar.addMenu(self.config.get("menu_help", "Help"))
        about_action = QAction("About DeviceForge Pro", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        QMessageBox.about(
            self,
            "About DeviceForge Pro",
            "DeviceForge Pro — Multi-Platform Servicing Framework\nVersion 1.0.0"
        )
