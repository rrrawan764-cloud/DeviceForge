from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict, Optional

class BaseHandler(QObject):
    """المعالج الأساسي لجميع البروتوكولات"""
    
    progress = pyqtSignal(str)
    device_detected = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.device_info = {}
        self.connected = False
        
    def detect_device(self) -> Dict:
        """كشف الجهاز - يجب توريثه"""
        raise NotImplementedError("يجب تنفيذ هذه الدالة في الفئة الفرعية")
    
    def connect_device(self, device_id: str) -> Dict:
        """الاتصال بالجهاز"""
        self.device_info['id'] = device_id
        self.connected = True
        return {'success': True, 'message': f'تم الاتصال بالجهاز {device_id}'}
    
    def disconnect_device(self) -> Dict:
        """فصل الجهاز"""
        self.connected = False
        return {'success': True, 'message': 'تم فصل الجهاز'}
    
    def flash_rom(self, device_id: str, rom_path: str, options: Dict = None) -> Dict:
        """فلاش ROM - يجب توريثه"""
        raise NotImplementedError("يجب تنفيذ هذه الدالة في الفئة الفرعية")
    
    def read_info(self, device_id: str) -> Dict:
        """قراءة معلومات الجهاز - يجب توريثه"""
        raise NotImplementedError("يجب تنفيذ هذه الدالة في الفئة الفرعية")
