import subprocess
import re
import usb.core
import usb.util
from typing import Optional, Dict, List


class DeviceInfo:
    """Container for detected device information."""

    def __init__(self):
        self.platform: str = ""           # android, ios, feature
        self.connection: str = ""          # adb, fastboot, edl, mtk, samsung, recovery, dfu
        self.vendor_id: str = ""
        self.product_id: str = ""
        self.serial: str = ""
        self.model: str = ""
        self.brand: str = ""
        self.android_version: str = ""
        self.battery: int = 0
        self.storage_total: int = 0
        self.storage_free: int = 0
        self.imei: str = ""
        self.rooted: bool = False
        self.bootloader_unlocked: bool = False
        self.cpu_abi: str = ""
        self.screen_resolution: str = ""
        self.kernel_version: str = ""
        self.build_number: str = ""
        self.radio_version: str = ""
        self.usb_info: Dict = {}

    def to_dict(self):
        return {
            "platform": self.platform,
            "connection": self.connection,
            "vendor_id": self.vendor_id,
            "product_id": self.product_id,
            "serial": self.serial,
            "model": self.model,
            "brand": self.brand,
            "android_version": self.android_version,
            "battery": self.battery,
            "storage_total": self.storage_total,
            "storage_free": self.storage_free,
            "imei": self.imei,
            "rooted": self.rooted,
            "bootloader_unlocked": self.bootloader_unlocked,
            "cpu_abi": self.cpu_abi,
            "screen_resolution": self.screen_resolution,
            "kernel_version": self.kernel_version,
            "build_number": self.build_number,
            "radio_version": self.radio_version,
        }


class DeviceDetector:
    """Detects connected devices across multiple protocols."""

    # Known USB vendor IDs
    VENDOR_IDS = {
        0x04E8: "Samsung",
        0x18D1: "Google",
        0x22B8: "Motorola",
        0x0BB4: "HTC",
        0x12D1: "Huawei",
        0x0FCE: "Sony",
        0x19D2: "ZTE",
        0x1BBF: "TCL",
        0x2A70: "OnePlus",
        0x2717: "Xiaomi",
        0x0E8D: "MediaTek",
        0x05C6: "Qualcomm",
        0x1782: "Spreadtrum",
        0x0409: "NEC",
        0x05AC: "Apple",
        0x0FC9: "Transsion/TECNO",
    }

    # Qualcomm EDL mode VID:PID
    EDL_IDS = {(0x05C6, 0x9008), (0x05C6, 0x900E)}
    # MediaTek BROM
    MTK_IDS = {(0x0E8D, p) for p in [0x0001, 0x2000, 0x2001]}
    # Samsung download mode
    SAMSUNG_IDS = {(0x04E8, p) for p in [0x6601, 0x6604, 0x685D, 0x681D]}

    def __init__(self, adb_path="tools/adb.exe", fastboot_path="tools/fastboot.exe"):
        self.adb_path = adb_path
        self.fastboot_path = fastboot_path

    def detect_all(self) -> List[DeviceInfo]:
        """Detect all connected devices across all protocols."""
        devices = []

        # ADB devices
        devices.extend(self._detect_adb())

        # Fastboot devices
        devices.extend(self._detect_fastboot())

        # USB raw devices (EDL, MTK, Samsung, DFU)
        devices.extend(self._detect_usb_raw())

        return devices

    def _run_command(self, cmd: List[str], timeout: int = 10) -> str:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _detect_adb(self) -> List[DeviceInfo]:
        devices = []
        output = self._run_command([self.adb_path, "devices"])

        for line in output.split("\n"):
            line = line.strip()
            if not line or "List of devices" in line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1].strip() == "device":
                serial = parts[0].strip()
                info = DeviceInfo()
                info.serial = serial
                info.connection = "adb"
                info.platform = "android"
                
                # Fetch detailed properties via adb shell
                info.model = self._run_command([self.adb_path, "-s", serial, "shell", "getprop", "ro.product.model"])
                info.brand = self._run_command([self.adb_path, "-s", serial, "shell", "getprop", "ro.product.brand"])
                info.android_version = self._run_command([self.adb_path, "-s", serial, "shell", "getprop", "ro.build.version.release"])
                
                devices.append(info)
        return devices

    def _detect_fastboot(self) -> List[DeviceInfo]:
        devices = []
        output = self._run_command([self.fastboot_path, "devices"])

        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2 and "fastboot" in parts[1].strip():
                serial = parts[0].strip()
                info = DeviceInfo()
                info.serial = serial
                info.connection = "fastboot"
                info.platform = "android"
                devices.append(info)
        return devices

    def _detect_usb_raw(self) -> List[DeviceInfo]:
        devices = []
        try:
            for bus in usb.core.find(find_all=True):
                vid = bus.idVendor
                pid = bus.idProduct
                if (vid, pid) in self.EDL_IDS:
                    info = DeviceInfo()
                    info.connection = "edl"
                    info.vendor_id = hex(vid)
                    info.brand = self.VENDOR_IDS.get(vid, "Qualcomm")
                    devices.append(info)
                elif (vid, pid) in self.MTK_IDS:
                    info = DeviceInfo()
                    info.connection = "mtk"
                    info.vendor_id = hex(vid)
                    info.brand = "MediaTek"
                    devices.append(info)
                elif (vid, pid) in self.SAMSUNG_IDS:
                    info = DeviceInfo()
                    info.connection = "samsung"
                    info.vendor_id = hex(vid)
                    info.brand = "Samsung"
                    devices.append(info)
        except Exception:
            pass
        return devices
