import subprocess
import os
import json
from datetime import datetime
from typing import Dict, List
from core.logger import Logger

class BackupManager:
    """مدير النسخ الاحتياطي للبيانات والملفات"""
    
    def __init__(self, backup_dir: str = "backups/"):
        self.backup_dir = backup_dir
        self.logger = Logger()
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, device_serial: str, backup_type: str = 'full') -> Dict:
        """إنشاء نسخة احتياطية"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"{device_serial}_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        self.logger.info(f"بدء النسخ الاحتياطي للجهاز {device_serial}")
        
        if backup_type == 'full':
            return self._full_backup(device_serial, backup_path)
        elif backup_type == 'apps':
            return self._apps_backup(device_serial, backup_path)
        elif backup_type == 'contacts':
            return self._contacts_backup(device_serial, backup_path)
        else:
            return {'status': 'error', 'message': f'نوع النسخ غير مدعوم: {backup_type}'}
    
    def _full_backup(self, serial: str, backup_path: str) -> Dict:
        """نسخ احتياطي كامل"""
        try:
            # نسخ ملفات النظام والتطبيقات
            result = subprocess.run(['adb', '-s', serial, 'backup', '-f', 
                                   f'{backup_path}/backup.ab', '-apk', '-shared', '-all', '-system'],
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                # حفظ معلومات إضافية
                info = {
                    'device_serial': serial,
                    'backup_date': datetime.now().isoformat(),
                    'backup_type': 'full',
                    'backup_path': backup_path
                }
                with open(f'{backup_path}/info.json', 'w') as f:
                    json.dump(info, f, indent=2)
                
                return {'status': 'success', 'message': 'تم النسخ الاحتياطي الكامل', 'path': backup_path}
            else:
                return {'status': 'error', 'message': result.stderr}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _apps_backup(self, serial: str, backup_path: str) -> Dict:
        """نسخ تطبيقات فقط"""
        try:
            result = subprocess.run(['adb', '-s', serial, 'shell', 'pm', 'list', 'packages'],
                                   capture_output=True, text=True)
            packages = [line.split(':')[1] for line in result.stdout.strip().split('\n') if line]
            
            apps_info = []
            for pkg in packages[:10]:  # فقط للتوضيح - يمكن زيادة العدد
                apps_info.append(pkg)
            
            # حفظ قائمة التطبيقات
            with open(f'{backup_path}/apps_list.json', 'w') as f:
                json.dump(apps_info, f, indent=2)
            
            return {'status': 'success', 'message': 'تم نسخ قائمة التطبيقات', 'app_count': len(apps_info)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _contacts_backup(self, serial: str, backup_path: str) -> Dict:
        """نسخ جهات الاتصال"""
        try:
            # تصدير جهات الاتصال عبر ADB
            result = subprocess.run(['adb', '-s', serial, 'shell', 'content', 'query', 
                                   '--uri', 'content://contacts/people/'],
                                   capture_output=True, text=True)
            
            contacts = []
            if result.returncode == 0:
                # تحليل الناتج (مبسط - يمكن تحسينه)
                lines = result.stdout.strip().split('\n')
                for line in lines[:20]:  # فقط للتوضيح
                    if line:
                        contacts.append(line)
            
            with open(f'{backup_path}/contacts.txt', 'w') as f:
                f.write('\n'.join(contacts))
            
            return {'status': 'success', 'message': 'تم نسخ جهات الاتصال', 'contact_count': len(contacts)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def restore_backup(self, backup_path: str) -> Dict:
        """استعادة نسخة احتياطية"""
        if not os.path.exists(backup_path):
            return {'status': 'error', 'message': 'مسار النسخ غير موجود'}
        
        # التحقق من وجود ملف المعلومات
        info_path = os.path.join(backup_path, 'info.json')
        if not os.path.exists(info_path):
            return {'status': 'error', 'message': 'ملف المعلومات غير موجود'}
        
        with open(info_path, 'r') as f:
            info = json.load(f)
        
        self.logger.info(f"استعادة النسخ الاحتياطي من {backup_path}")
        
        backup_file = os.path.join(backup_path, 'backup.ab')
        if os.path.exists(backup_file):
            try:
                result = subprocess.run(['adb', 'restore', backup_file], capture_output=True, text=True)
                if result.returncode == 0:
                    return {'status': 'success', 'message': 'تم استعادة النسخ الاحتياطي'}
                else:
                    return {'status': 'error', 'message': result.stderr}
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        else:
            return {'status': 'error', 'message': 'ملف النسخ غير موجود'}
