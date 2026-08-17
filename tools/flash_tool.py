import subprocess
import os
import threading
from typing import Optional, Dict
from core.logger import Logger

class FlashTool:
    """أداة فلاش ROMs والملفات النظامية"""
    
    def __init__(self):
        self.logger = Logger()
        self.flash_thread = None
        self.is_flashing = False
        
    def flash_rom(self, device_serial: str, rom_path: str, flash_type: str = 'fastboot') -> Dict:
        """فلاش ROM على الجهاز"""
        if not os.path.exists(rom_path):
            return {'status': 'error', 'message': f'مسار ROM غير موجود: {rom_path}'}
        
        self.is_flashing = True
        self.logger.info(f"بدء فلاش ROM: {rom_path} على الجهاز {device_serial}")
        
        if flash_type == 'fastboot':
            result = self._flash_fastboot(device_serial, rom_path)
        elif flash_type == 'adb':
            result = self._flash_adb(device_serial, rom_path)
        else:
            result = {'status': 'error', 'message': f'نوع الفلاش غير مدعوم: {flash_type}'}
        
        self.is_flashing = False
        return result
    
    def _flash_fastboot(self, serial: str, rom_path: str) -> Dict:
        """الفلاش عبر Fastboot"""
        try:
            commands = [
                ['fastboot', '-s', serial, 'flash', 'boot', f'{rom_path}/boot.img'],
                ['fastboot', '-s', serial, 'flash', 'system', f'{rom_path}/system.img'],
                ['fastboot', '-s', serial, 'flash', 'userdata', f'{rom_path}/userdata.img']
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    return {'status': 'error', 'message': result.stderr}
            
            return {'status': 'success', 'message': 'تم فلاش ROM بنجاح'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _flash_adb(self, serial: str, rom_path: str) -> Dict:
        """الفلاش عبر ADB (نادر الاستخدام)"""
        return {'status': 'error', 'message': 'الفلاش عبر ADB غير مدعوم حالياً'}
    
    def flash_partition(self, serial: str, partition: str, image_path: str) -> Dict:
        """فلاش بارتشن معين"""
        if not os.path.exists(image_path):
            return {'status': 'error', 'message': f'ملف الصورة غير موجود: {image_path}'}
        
        try:
            cmd = ['fastboot', '-s', serial, 'flash', partition, image_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {'status': 'success', 'message': f'تم فلاش {partition} بنجاح'}
            else:
                return {'status': 'error', 'message': result.stderr}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
