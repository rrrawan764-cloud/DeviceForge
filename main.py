import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTextCodec
from core.config import ConfigManager
from core.logger import DeviceForgeLogger
from ui.main_window import MainWindow


def main():
    # Initialize Application
    app = QApplication(sys.argv)

    # Initialize Core Managers
    config_manager = ConfigManager()
    logger = DeviceForgeLogger(log_dir=config_manager.get_setting("log_dir", "logs"))

    logger.info("Starting DeviceForge Pro application...")

    # Load Dark Theme / Stylesheet if available
    style_path = "ui/styles/dark_theme.qss"
    if os.path.exists(style_path):
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            logger.info("Dark theme stylesheet loaded successfully.")
        except Exception as e:
            logger.warning(f"Failed to load stylesheet: {e}")

    # Create and Show Main Window
    main_window = MainWindow(config_manager, logger)
    main_window.show()

    logger.info("DeviceForge Pro GUI is now running.")

    # Execute Application Event Loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
