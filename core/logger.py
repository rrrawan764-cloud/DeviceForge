import logging
import os
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class LogSignal(QObject):
    """Qt signal bridge for UI log display."""
    log_emitted = pyqtSignal(str, str)  # level, message


class DeviceForgeLogger:
    """Centralized logging with file output and UI signal support."""

    def __init__(self, log_dir="logs", name="DeviceForge"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self.signal = LogSignal()

        log_file = os.path.join(
            log_dir,
            f"deviceforge_{datetime.now().strftime('%Y%m%d')}.log"
        )

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()

        # File handler
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        self.logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter(
            "[%(levelname)s] %(message)s"
        ))
        self.logger.addHandler(ch)

    def _emit(self, level, msg):
        self.signal.log_emitted.emit(level, msg)

    def debug(self, msg):
        self.logger.debug(msg)
        self._emit("DEBUG", msg)

    def info(self, msg):
        self.logger.info(msg)
        self._emit("INFO", msg)

    def warning(self, msg):
        self.logger.warning(msg)
        self._emit("WARNING", msg)

    def error(self, msg):
        self.logger.error(msg)
        self._emit("ERROR", msg)

    def critical(self, msg):
        self.logger.critical(msg)
        self._emit("CRITICAL", msg)

    def get_log_files(self):
        logs = []
        if os.path.exists(self.log_dir):
            logs = [
                os.path.join(self.log_dir, f)
                for f in os.listdir(self.log_dir)
                if f.endswith(".log")
            ]
        return sorted(logs)

    def export_log(self, output_path, log_file=None):
        if log_file is None:
            files = self.get_log_files()
            if not files:
                return False
            log_file = files[-1]

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            self.error(f"Failed to export log: {e}")
            return False
