# nano ui/widgets/backup_panel.py

"""
DeviceForge Pro — Backup Panel Widget
Professional device backup/restore management with protocol-aware support.
Handles full, partial, encrypted, and differential backups across all supported device protocols.
"""

import os
import json
import time
import shutil
import hashlib
import platform
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, List, Tuple

from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QSize, QRect, QPoint
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QProgressBar, QComboBox, QCheckBox, QLineEdit,
    QTextEdit, QFileDialog, QGroupBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QSlider, QSpinBox, QMessageBox,
    QFrame, QScrollArea, QToolButton, QMenu, QAction, QSizePolicy,
    QStyledItemDelegate, QStyleOptionViewItem
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QPen,
    QLinearGradient, QBrush, QTextCursor, QFontDatabase
)

from core.logger import DeviceForgeLogger
from core.config import ConfigManager


# ──────────────────────────────────────────────
# Enums & Data Models
# ──────────────────────────────────────────────

class BackupType(Enum):
    FULL = auto()
    PARTIAL = auto()
    INCREMENTAL = auto()
    DIFFERENTIAL = auto()
    SYSTEM_ONLY = auto()
    USER_DATA = auto()
    APP_DATA = auto()
    ENCRYPTED = auto()


class BackupStatus(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    COMPRESSING = "compressing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RESTORING = "restoring"


class ProtocolType(Enum):
    ADB = "android_adb"
    FASTBOOT = "android_fastboot"
    EDL = "qualcomm_edl"
    MTK_BROM = "mediatek_brom"
    MTK_PRELOADER = "mediatek_preloader"
    MTK_META = "mediatek_meta"
    SAMSUNG_DOWNLOAD = "samsung_download"
    SAMSUNG_MODEM = "samsung_modem"
    APPLE_DFU = "apple_dfu"
    APPLE_RECOVERY = "apple_recovery"
    APPLE_NORMAL = "apple_normal"
    UNISOC_DOWNLOAD = "unisoc_download"
    UNISOC_DIAG = "unisoc_diag"


@dataclass
class BackupPartition:
    name: str
    size_bytes: int
    offset: int = 0
    mount_point: str = ""
    filesystem: str = ""
    selected: bool = True
    backed_up: bool = False
    hash_sha256: str = ""
    error: str = ""

    @property
    def size_human(self) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self.size_bytes < 1024.0:
                return f"{self.size_bytes:.2f} {unit}"
            self.size_bytes /= 1024.0
        return f"{self.size_bytes:.2f} PB"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "size_bytes": self.size_bytes,
            "offset": self.offset,
            "mount_point": self.mount_point,
            "filesystem": self.filesystem,
            "selected": self.selected,
            "hash_sha256": self.hash_sha256,
        }


@dataclass
class BackupManifest:
    device_model: str = ""
    device_serial: str = ""
    protocol: str = ""
    backup_type: str = ""
    created_at: str = ""
    completed_at: str = ""
    partitions: List[BackupPartition] = field(default_factory=list)
    total_size: int = 0
    encrypted: bool = False
    compression: str = "none"
    checksum_verified: bool = False
    software_version: str = ""
    android_version: str = ""
    ios_version: str = ""
    notes: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "device_model": self.device_model,
            "device_serial": self.device_serial,
            "protocol": self.protocol,
            "backup_type": self.backup_type,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "partitions": [p.to_dict() for p in self.partitions],
            "total_size": self.total_size,
            "encrypted": self.encrypted,
            "compression": self.compression,
            "checksum_verified": self.checksum_verified,
            "software_version": self.software_version,
            "android_version": self.android_version,
            "ios_version": self.ios_version,
            "notes": self.notes,
        }, indent=4, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: str) -> "BackupManifest":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        manifest = cls(
            device_model=data.get("device_model", ""),
            device_serial=data.get("device_serial", ""),
            protocol=data.get("protocol", ""),
            backup_type=data.get("backup_type", ""),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at", ""),
            total_size=data.get("total_size", 0),
            encrypted=data.get("encrypted", False),
            compression=data.get("compression", "none"),
            checksum_verified=data.get("checksum_verified", False),
            software_version=data.get("software_version", ""),
            android_version=data.get("android_version", ""),
            ios_version=data.get("ios_version", ""),
            notes=data.get("notes", ""),
        )
        manifest.partitions = [
            BackupPartition(
                name=p["name"],
                size_bytes=p["size_bytes"],
                offset=p.get("offset", 0),
                mount_point=p.get("mount_point", ""),
                filesystem=p.get("filesystem", ""),
                hash_sha256=p.get("hash_sha256", ""),
            )
            for p in data.get("partitions", [])
        ]
        return manifest


# ──────────────────────────────────────────────
# Backup Worker Thread
# ──────────────────────────────────────────────

class BackupWorker(QThread):
    progress_updated = pyqtSignal(int, str)       # percentage, message
    partition_started = pyqtSignal(str)            # partition name
    partition_completed = pyqtSignal(str, str)     # partition name, sha256
    partition_failed = pyqtSignal(str, str)        # partition name, error
    status_changed = pyqtSignal(BackupStatus)
    backup_finished = pyqtSignal(bool, str)        # success, output_path
    log_message = pyqtSignal(str, str)             # level, message

    def __init__(
        self,
        protocol: ProtocolType,
        backup_type: BackupType,
        output_dir: str,
        partitions: List[BackupPartition],
        device_serial: str = "",
        device_model: str = "",
        encrypt: bool = False,
        password: str = "",
        compression: str = "none",
        parent=None
    ):
        super().__init__(parent)
        self._logger = DeviceForgeLogger("BackupWorker")
        self._cancel_flag = threading.Event()
        self.protocol = protocol
        self.backup_type = backup_type
        self.output_dir = Path(output_dir)
        self.partitions = partitions
        self.device_serial = device_serial
        self.device_model = device_model
        self.encrypt = encrypt
        self.password = password
        self.compression = compression

    def cancel(self):
        self._cancel_flag.set()
        self.status_changed.emit(BackupStatus.CANCELLED)

    def _is_cancelled(self) -> bool:
        return self._cancel_flag.is_set()

    def _run_adb_backup(self) -> Tuple[bool, str]:
        """ADB-based backup for Android devices in normal mode."""
        self.log_message.emit("INFO", f"Starting ADB backup for {self.device_model}")
        self.status_changed.emit(BackupStatus.SCANNING)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"adb_backup_{self.device_serial or 'unknown'}_{timestamp}"
        backup_path = self.output_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)

        manifest = BackupManifest(
            device_model=self.device_model,
            device_serial=self.device_serial,
            protocol=self.protocol.value,
            backup_type=self.backup_type.name,
            created_at=datetime.now().isoformat(),
            compression=self.compression,
            encrypted=self.encrypt,
        )

        total = len(self.partitions)
        for idx, part in enumerate(self.partitions):
            if self._is_cancelled():
                self.backup_finished.emit(False, "Cancelled by user")
                return False, "Cancelled"

            if not part.selected:
                continue

            self.partition_started.emit(part.name)
            self.status_changed.emit(BackupStatus.IN_PROGRESS)
            self.progress_updated.emit(
                int((idx / total) * 100),
                f"Backing up {part.name} ({part.size_human})..."
            )

            try:
                part_file = backup_path / f"{part.name}.img"

                if part.mount_point:
                    cmd = [
                        "adb", "-s", self.device_serial,
                        "shell", "dd", f"if={part.mount_point}",
                        "bs=4M"
                    ]
                else:
                    cmd = [
                        "adb", "-s", self.device_serial,
                        "shell", "dd", f"if=/dev/block/by-name/{part.name}",
                        "bs=4M"
                    ]

                self.log_message.emit("DEBUG", f"Executing: {' '.join(cmd)}")

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                )

                sha = hashlib.sha256()
                bytes_written = 0

                with open(part_file, "wb") as f:
                    while True:
                        if self._is_cancelled():
                            process.kill()
                            self.backup_finished.emit(False, "Cancelled")
                            return False, "Cancelled"

                        chunk = process.stdout.read(4096 * 16)
                        if not chunk:
                            break
                        f.write(chunk)
                        sha.update(chunk)
                        bytes_written += len(chunk)
                        pct = int(((idx + (bytes_written / max(part.size_bytes, 1))) / total) * 100)
                        self.progress_updated.emit(
                            min(pct, 99),
                            f"Reading {part.name}: {bytes_written / (1024*1024):.1f} MB"
                        )

                process.wait(timeout=30)
                part.backed_up = True
                part.hash_sha256 = sha.hexdigest()
                manifest.partitions.append(part)
                manifest.total_size += bytes_written
                self.partition_completed.emit(part.name, part.hash_sha256)

            except subprocess.TimeoutExpired:
                part.error = "Timeout reading partition"
                self.partition_failed.emit(part.name, part.error)
                self.log_message.emit("ERROR", f"Timeout on {part.name}")
            except Exception as e:
                part.error = str(e)
                self.partition_failed.emit(part.name, part.error)
                self.log_message.emit("ERROR", f"Failed {part.name}: {e}")

        manifest.completed_at = datetime.now().isoformat()

        manifest_path = backup_path / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.to_json())

        if self.compression != "none":
            self.status_changed.emit(BackupStatus.COMPRESSING)
            self._compress_backup(backup_path, self.compression)

        if self.encrypt:
            self.status_changed.emit(BackupStatus.VERIFYING)
            self._encrypt_backup(backup_path, self.password)

        self.status_changed.emit(BackupStatus.COMPLETED)
        self.backup_finished.emit(True, str(backup_path))
        return True, str(backup_path)

    def _run_edl_backup(self) -> Tuple[bool, str]:
        """Qualcomm EDL (Emergency Download) mode backup via firehose programmer."""
        self.log_message.emit("INFO", f"Starting EDL backup")
        self.status_changed.emit(BackupStatus.SCANNING)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"edl_backup_{timestamp}"
        backup_path = self.output_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)

        manifest = BackupManifest(
            protocol=self.protocol.value,
            backup_type=self.backup_type.name,
            created_at=datetime.now().isoformat(),
            compression=self.compression,
            encrypted=self.encrypt,
        )

        # EDL uses firehose protocol — read GPT headers first
        gpt_path = backup_path / "gpt_main.bin"
        try:
            self.progress_updated.emit(5, "Reading GPT partition table via firehose...")

            # Simulated firehose read — in production this interfaces with
            # the Qualcomm QPST/QRD firehose programmer binary
            gpt_cmd = [
                "fh_loader", "--port=\\\\.\\COM3",
                "--send_image=gpt_main.bin",
                f"--output={gpt_path}",
                "--zlp=1"
            ]
            self.log_message.emit("DEBUG", f"Firehose GPT read: {' '.join(gpt_cmd)}")

            # Parse GPT to populate partition list if not provided
            if not self.partitions:
                self._parse_gpt_partitions(gpt_path)

        except Exception as e:
            self.log_message.emit("ERROR", f"GPT read failed: {e}")
            self.backup_finished.emit(False, f"GPT read failed: {e}")
            return False, str(e)

        total = len(self.partitions)
        for idx, part in enumerate(self.partitions):
            if self._is_cancelled():
                return False, "Cancelled"

            if not part.selected:
                continue

            self.partition_started.emit(part.name)
            self.status_changed.emit(BackupStatus.IN_PROGRESS)

            part_file = backup_path / f"{part.name}.bin"
            try:
                # Firehose read command
                read_cmd = [
                    "fh_loader", "--port=\\\\.\\COM3",
                    f"--read_image={part.name}",
                    f"--output={part_file}",
                    f"--start_sector={part.offset // 512}",
                    f"--num_sectors={part.size_bytes // 512}",
                    "--zlp=1"
                ]
                self.log_message.emit("DEBUG", f"EDL read {part.name}: {' '.join(read_cmd)}")

                process = subprocess.Popen(
                    read_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                )

                sha = hashlib.sha256()
                with open(part_file, "wb") as f:
                    for chunk in iter(lambda: process.stdout.read(4096 * 16), b''):
                        if self._is_cancelled():
                            process.kill()
                            return False, "Cancelled"
                        f.write(chunk)
                        sha.update(chunk)

                process.wait(timeout=120)
                part.hash_sha256 = sha.hexdigest()
                part.backed_up = True
                manifest.partitions.append(part)
                manifest.total_size += part.size_bytes
                self.partition_completed.emit(part.name, part.hash_sha256)
                self.progress_updated.emit(int((idx / total) * 100), f"EDL: {part.name} done")

            except Exception as e:
                part.error = str(e)
                self.partition_failed.emit(part.name, part.error)
                self.log_message.emit("ERROR", f"EDL read failed {part.name}: {e}")

        manifest.completed_at = datetime.now().isoformat()
        with open(backup_path / "manifest.json", "w", encoding="utf-8") as f:
            f.write(manifest.to_json())

        self.status_changed.emit(BackupStatus.COMPLETED)
        self.backup_finished.emit(True, str(backup_path))
        return True, str(backup_path)

    def _run_mtk_backup(self) -> Tuple[bool, str]:
        """MediaTek BROM/Preloader/META mode backup."""
        self.log_message.emit("INFO", f"Starting MediaTek backup via {self.protocol.value}")
        self.status_changed.emit(BackupStatus.SCANNING)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"mtk_backup_{timestamp}"
        backup_path = self.output_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)

        manifest = BackupManifest(
            protocol=self.protocol.value,
            backup_type=self.backup_type.name,
            created_at=datetime.now().isoformat(),
        )

        # MTK uses SP Flash Tool / mtkclient protocol
        mtk_cmd_base = ["mtk", "rl", "all", str(backup_path)]

        if self.protocol == ProtocolType.MTK_BROM:
            mtk_cmd_base = ["mtk", "brom", "rl", "all", str(backup_path)]
        elif self.protocol == ProtocolType.MTK_META:
            mtk_cmd_base = ["mtk", "meta", "rl", "all", str(backup_path)]

        self.log_message.emit("DEBUG", f"MTK command: {' '.join(mtk_cmd_base)}")

        try:
            process = subprocess.Popen
