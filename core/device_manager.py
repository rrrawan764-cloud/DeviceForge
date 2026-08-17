import usb.core
import usb.util
import serial.tools.list_ports
import subprocess
import threading
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict


class Platform(Enum):
    ANDROID_ADB = "android_adb"
    ANDROID_FASTBOOT = "android_fastboot"
    ANDROID_RECOVERY = "android_recovery"
    QUALCOMM_EDL = "qualcomm_edl"
    MEDIATEK_BROM = "mediatek_brom"
    MEDIATEK_META = "mediatek_meta"
    MEDIATEK_PRELOADER = "mediatek_preloader"
    UNISOC_DIAG = "unisoc_diag"
    UNISOC_DOWNLOAD = "unisoc_download"
    SAMSUNG_DOWNLOAD = "samsung_download"
    SAMSUNG_MODEM = "samsung_modem"
    APPLE_DFU = "apple_dfu"
    APPLE_RECOVERY = "apple_recovery"
    APPLE_NORMAL = "apple_normal"
    UNKNOWN = "unknown"


@dataclass
class DeviceInfo:
    platform: Platform
    vid: int = 0
    pid: int = 0
    serial_number: str = ""
    com_port: str = ""
    manufacturer: str = ""
    model: str = ""
    chipset: str = ""
    firmware_version: str = ""
    battery_level: int = 0
    storage_total: int = 0
    storage_used: int = 0
    imei_primary: str = ""
    imei_secondary: str = ""
    is_rooted: bool = False
    bootloader_unlocked: bool = False
    connection_time: float = field(default_factory=time.time)


class DeviceManager:
    """Central device detection and lifecycle management"""
    
    # USB VID/PID mappings for all supported platforms
    USB_DEVICE_MAP = {
        # Qualcomm EDL Mode (Emergency Download)
        (0x05C6, 0x9008): Platform.QUALCOMM_EDL,
        (0x05C6, 0x900E): Platform.QUALCOMM_EDL,
        (0x05C6, 0x9025): Platform.QUALCOMM_EDL,  # QFIL secondary
        
        # MediaTek BootROM
        (0x0E8D, 0x0003): Platform.MEDIATEK_BROM,
        (0x0E8D, 0x2000): Platform.MEDIATEK_BROM,  # Newer chipsets
        (0x0E8D, 0x2001): Platform.MEDIATEK_PRELOADER,
        
        # MediaTek META Mode
        (0x0E8D, 0x2007): Platform.MEDIATEK_META,
        (0x0E8D, 0x2004): Platform.MEDIATEK_META,
        
        # Unisoc / Spreadtrum
        (0x1782, 0x4D00): Platform.UNISOC_DOWNLOAD,
        (0x1782, 0x4D02): Platform.UNISOC_DIAG,
        (0x1782, 0x4D04): Platform.UNISOC_DIAG,
        (0x1782, 0x4D07): Platform.UNISOC_DOWNLOAD,
        (0x1782, 0x4D0A): Platform.UNISOC_DIAG,
        (0x1782, 0x4D0D): Platform.UNISOC_DIAG,
        (0x1782, 0x4D14): Platform.UNISOC_DOWNLOAD,
        
        # Samsung Download Mode (Odin)
        (0x04E8, 0x685D): Platform.SAMSUNG_DOWNLOAD,
        (0x04E8, 0x685E): Platform.SAMSUNG_DOWNLOAD,  # Older models
        (0x04E8, 0x6860): Platform.SAMSUNG_DOWNLOAD,
        
        # Apple Devices
        (0x05AC, 0x1227): Platform.APPLE_DFU,
        (0x05AC, 0x1281): Platform.APPLE_RECOVERY,
        (0x05AC, 0x1294): Platform.APPLE_RECOVERY,  # A10 Fusion
        
        # Google Fastboot
        (0x18D1, 0xD00D): Platform.ANDROID_FASTBOOT,
        (0x18D1, 0x4EE7): Platform.ANDROID_ADB,
        (0x18D1, 0x4EE0): Platform.ANDROID_FASTBOOT,
    }
    
    def __init__(self):
        self.devices: List[DeviceInfo] = []
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False
        self._callbacks: List[callable] = []
        self._adb_path = "adb"
        self._fastboot_path = "fastboot"
        
    def register_callback(self, callback: callable):
        """Register callback for device connect/disconnect events"""
        self._callbacks.append(callback)
    
    def start_monitoring(self):
        """Start USB device monitoring in background thread"""
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            daemon=True,
            name="DeviceMonitor"
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Continuous device scanning loop"""
        known_serials = set()
        
        while self._running:
            current_devices = self._scan_all_platforms()
            current_serials = {d.serial_number or f"{d.vid}:{d.pid}:{d.com_port}" 
                             for d in current_devices}
            
            # Detect new connections
            new_serials = current_serials - known_serials
            if new_serials:
                for device in current_devices:
                    dev_key = device.serial_number or f"{device.vid}:{device.pid}:{device.com_port}"
                    if dev_key in new_serials:
                        self._notify_callbacks("connected", device)
            
            # Detect disconnections
            removed_serials = known_serials - current_serials
            if removed_serials:
                for serial in removed_serials:
                    removed_device = next(
                        (d for d in self.devices 
                         if (d.serial_number or f"{d.vid}:{d.pid}:{d.com_port}") == serial),
                        None
                    )
                    if removed_device:
                        self._notify_callbacks("disconnected", removed_device)
            
            self.devices = current_devices
            known_serials = current_serials
            time.sleep(1.5)  # Poll interval
    
    def _scan_all_platforms(self) -> List[DeviceInfo]:
        """Scan all supported platform interfaces"""
        devices = []
        devices.extend(self._scan_usb_devices())
        devices.extend(self._scan_com_ports())
        devices.extend(self._scan_adb_devices())
        devices.extend(self._scan_fastboot_devices())
        return devices
    
    def _scan_usb_devices(self) -> List[DeviceInfo]:
        """Scan USB bus for known device signatures"""
        devices = []
        try:
            for dev in usb.core.find(find_all=True):
                vid = dev.idVendor
                pid = dev.idProduct
                
                if (vid, pid) in self.USB_DEVICE_MAP:
                    platform = self.USB_DEVICE_MAP[(vid, pid)]
                    
                    device_info = DeviceInfo(
                        platform=platform,
                        vid=vid,
                        pid=pid
                    )
                    
                    # Try to get serial number
                    try:
                        if dev.serial_number:
                            device_info.serial_number = dev.serial_number
                    except:
                        pass
                    
                    # Try to get manufacturer
                    try:
                        if dev.manufacturer:
                            device_info.manufacturer = dev.manufacturer
                    except:
                        pass
                    
                    # Try to get product name
                    try:
                        if dev.product:
                            device_info.model = dev.product
                    except:
                        pass
                    
                    devices.append(device_info)
        except usb.core.NoBackendError:
            pass
        except Exception as e:
            print(f"USB scan error: {e}")
        
        return devices
    
    def _scan_com_ports(self) -> List[DeviceInfo]:
        """Scan COM ports for serial-based connections"""
        devices = []
        
        for port in serial.tools.list_ports.comports():
            vid = port.vid if port.vid else 0
            pid = port.pid if port.pid else 0
            
            # MediaTek BROM / Preloader detection
            if vid == 0x0E8D and pid in (0x0003, 0x2000, 0x2001):
                platform = Platform.MEDIATEK_BROM if pid != 0x2001 else Platform.MEDIATEK_PRELOADER
                devices.append(DeviceInfo(
                    platform=platform,
                    vid=vid,
                    pid=pid,
                    com_port=port.device,
                    manufacturer=port.description
                ))
            
            # MediaTek META detection
            elif vid == 0x0E8D and pid in (0x2007, 0x2004):
                devices.append(DeviceInfo(
                    platform=Platform.MEDIATEK_META,
                    vid=vid,
                    pid=pid,
                    com_port=port.device,
                    manufacturer=port.description
                ))
            
            # Unisoc SPD detection
            elif vid == 0x1782:
                if "diag" in port.description.lower():
                    platform = Platform.UNISOC_DIAG
                else:
                    platform = Platform.UNISOC_DOWNLOAD
                devices.append(DeviceInfo(
                    platform=platform,
                    vid=vid,
                    pid=pid,
                    com_port=port.device,
                    manufacturer=port.description
                ))
            
            # Qualcomm EDL detection via COM port
            elif vid == 0x05C6 and pid == 0x9008:
                devices.append(DeviceInfo(
                    platform=Platform.QUALCOMM_EDL,
                    vid=vid,
                    pid=pid,
                    com_port=port.device,
                    manufacturer=port.description
                ))
            
            # Samsung Modem/Diag port detection
            elif vid == 0x04E8 and "modem" in port.description.lower():
                devices.append(DeviceInfo(
                    platform=Platform.SAMSUNG_MODEM,
                    vid=vid,
                    pid=pid,
                    com_port=port.device,
                    manufacturer=port.description
                ))
        
        return devices
