from typing import Dict, Optional
from core.device_detector import DeviceDetector
from core.logger import Logger

class DeviceManager:
    """مدير الأجهزة - التعامل مع الأجهزة المتصلة"""
    
    def __init__(self):
        self.detector = DeviceDetector()
        self.logger = Logger()
        self.current_device = None
        self.all_devices = {}
    
    def scan_devices(self) -> Dict:
        """مسح جميع الأجهزة المتصلة"""
        self.all_devices = self.detector.detect_all_devices()
        self.logger.info(f"تم مسح {len(self.all_devices.get('adb', []))} جهاز ADB")
        return self.all_devices
    
    def select_device(self, serial: str) -> bool:
        """اختيار جهاز معين للعمل عليه"""
        all_serial = []
        for device_type, devices in self.all_devices.items():
            if isinstance(devices, list):
                for device in devices:
                    if device.get('serial') == serial:
                        self.current_device = device
                        self.logger.info(f"تم اختيار الجهاز: {serial}")
                        return True
        self.logger.error(f"الجهاز {serial} غير موجود")
        return False
    
    def get_device_info(self) -> Dict:
        """الحصول على معلومات الجهاز المختار"""
        if not self.current_device:
            return {'error': 'لم يتم اختيار أي جهاز'}
        
        info = {'serial': self.current_device.get('serial')}
        
        if self.current_device.get('status') == 'device':
            # جهاز ADB - الحصول على معلومات إضافية
            try:
                import subprocess
                result = subprocess.run(['adb', '-s', info['serial'], 'shell', 'getprop', 'ro.product.model'],
                                      capture_output=True, text=True)
                info['model'] = result.stdout.strip()
                
                result = subprocess.run(['adb', '-s', info['serial'], 'shell', 'getprop', 'ro.build.version.release'],
                                      capture_output=True, text=True)
                info['android_version'] = result.stdout.strip()
            except Exception as e:
                info['error'] = str(e)
        
        return info
