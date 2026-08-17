نimport subprocess
import json

class DeviceInfo:
    def __init__(self, model, brand, android_version, serial, battery, storage_total, imei, rooted, bootloader_unlocked, connection):
        self.model = model
        self.brand = brand
        self.android_version = android_version
        self.serial = serial
        self.battery = battery
        self.storage_total = storage_total
        self.imei = imei
        self.rooted = rooted
        self.bootloader_unlocked = bootloader_unlocked
        self.connection = connection

    def to_dict(self):
        return self.__dict__


class DeviceDetector:
    """Detects both Android (ADB/Fastboot) and iOS (iPhone/iPad) devices."""

    def __init__(self, adb_path="adb", fastboot_path="fastboot"):
        self.adb_path = adb_path
        self.fastboot_path = fastboot_path

    def detect_all(self):
        devices = []
        
        # 1. Detect Android ADB Devices
        try:
            res = subprocess.run([self.adb_path, "devices"], capture_output=True, text=True, timeout=5)
            lines = res.stdout.strip().split("\n")[1:]
            for line in lines:
                if "\tdevice" in line:
                    serial = line.split("\t")[0]
                    # Fetch basic properties
                    model = subprocess.run([self.adb_path, "-s", serial, "shell", "getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
                    brand = subprocess.run([self.adb_path, "-s", serial, "shell", "getprop", "ro.product.brand"], capture_output=True, text=True).stdout.strip()
                    android_ver = subprocess.run([self.adb_path, "-s", serial, "shell", "getprop", "ro.build.version.release"], capture_output=True, text=True).stdout.strip()
                    
                    devices.append(DeviceInfo(
                        model=model or "Android Device",
                        brand=brand or "Unknown",
                        android_version=android_ver or "N/A",
                        serial=serial,
                        battery="N/A",
                        storage_total="N/A",
                        imei="N/A",
                        rooted="Unknown",
                        bootloader_unlocked="Unknown",
                        connection="adb"
                    ))
        except Exception:
            pass

        # 2. Detect iOS (iPhone / iPad) Devices
        try:
            res = subprocess.run(["idevice_id", "-l"], capture_output=True, text=True, timeout=5)
            ios_serials = res.stdout.strip().split("\n")
            for serial in ios_serials:
                if serial.strip():
                    # Fetch iOS device name/model via ideviceinfo
                    product_name = subprocess.run(["ideviceinfo", "-u", serial, "-k", "ProductType"], capture_output=True, text=True).stdout.strip()
                    device_name = subprocess.run(["ideviceinfo", "-u", serial, "-k", "DeviceName"], capture_output=True, text=True).stdout.strip()
                    ios_version = subprocess.run(["ideviceinfo", "-u", serial, "-k", "ProductVersion"], capture_output=True, text=True).stdout.strip()
                    
                    devices.append(DeviceInfo(
                        model=f"{device_name} ({product_name})",
                        brand="Apple",
                        android_version=f"iOS {ios_version}",
                        serial=serial.strip(),
                        battery="Healthy",
                        storage_total="N/A",
                        imei="N/A",
                        rooted="No (iOS)",
                        bootloader_unlocked="Locked",
                        connection="usb-ios"
                    ))
        except Exception:
            pass

        return devices

