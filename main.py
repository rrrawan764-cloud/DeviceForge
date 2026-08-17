import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from ui.translations import TranslationManager
from core.device_manager import DeviceManager

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    app = QApplication(sys.argv)
    app.setApplicationName("DeviceForge")
    app.setStyle("Fusion")
    
    # Initialize translation manager
    translator = TranslationManager()
    translator.load_language('ar')  # Default to Arabic
    
    # Initialize device manager
    device_manager = DeviceManager()
    device_manager.start_monitoring()
    
    # Launch main window
    window = MainWindow(translator, device_manager)
    window.show()
    
    sys.exit(app.exec_())
