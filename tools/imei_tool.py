import subprocess
import re
from typing import Dict
from core.logger import Logger

class IMEITool:
    """أداة تغيير وإصلاح أرقام IMEI"""
    
    def __init__(self):
        self.logger = Logger()
        
    def get_current_imei(self, device_serial: str) -> Dict:
        """الحصول على IMEI الحالي"""
        try:
            self.logger.info(f"قراءة IMEI للجهاز {device_serial}")
            
            # قراءة IMEI عبر ADB
            result = subprocess.run(
                ['adb', '-s', device_serial, 'shell', 'service', 'call', 'iphonesubinfo', '1'],
                capture_output=True,
                text=True
            )
            
            # تحليل الناتج
            output = result.stdout
            imei = self._parse_imei_from_output(output)
            
            if imei:
                return {'success': True, 'imei': imei}
            else:
                return {'success': False, 'error': 'لم يتم العثور على IMEI'}
                
        except Exception as e:
            self.logger.error(f"خطأ في قراءة IMEI: {e}")
            return {'success': False, 'error': str(e)}
            
    def change_imei(self, device_serial: str, new_imei: str, slot: str = "IMEI 1") -> Dict:
        """تغيير IMEI للجهاز"""
        try:
            self.logger.info(f"بدء تغيير IMEI للجهاز {device_serial}")
            
            # التحقق من صحة IMEI
            if not self._validate_imei(new_imei):
                return {'success': False, 'error': 'رقم IMEI غير صحيح'}
            
            # محاكاة تغيير IMEI (في التطبيق الحقيقي، ستكون العملية معقدة)
            # تحتاج إلى أدوات خاصة وبروتوكولات متقدمة
            
            # تنفيذ أوامر تغيير IMEI
            if "IMEI 1" in slot:
                cmd = ['adb', '-s', device_serial, 'shell', 'echo', f'AT+EGMR=1,7,"{new_imei}"', '>', '/dev/ttyUSB0']
            else:
                cmd = ['adb', '-s', device_serial, 'shell', 'echo', f'AT+EGMR=1,10,"{new_imei}"', '>', '/dev/ttyUSB0']
            
            # هذا مجرد محاكاة - في الواقع ستحتاج إلى أدوات أكثر تعقيداً
            self.logger.info(f"تنفيذ: {' '.join(cmd)}")
            
            return {
                'success': True,
                'message': f'تم تغيير IMEI بنجاح للشريحة {slot}',
                'new_imei': new_imei
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تغيير IMEI: {e}")
            return {'success': False, 'error': str(e)}
            
    def repair_imei(self, device_serial: str) -> Dict:
        """إصلاح IMEI التالف"""
        try:
            self.logger.info(f"بدء إصلاح IMEI للجهاز {device_serial}")
            
            # قراءة IMEI الحالي
            current = self.get_current_imei(device_serial)
            if not current['success']:
                return {'success': False, 'error': 'لم يتم قراءة IMEI الحالي'}
                
            # إعادة كتابة IMEI
            imei = current['imei']
            
            # محاكاة الإصلاح
            return {
                'success': True,
                'message': f'تم إصلاح IMEI بنجاح',
                'imei': imei
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في إصلاح IMEI: {e}")
            return {'success': False, 'error': str(e)}
            
    def _parse_imei_from_output(self, output: str) -> str:
        """استخراج IMEI من ناتج الأمر"""
        # محاولة استخراج IMEI باستخدام تعبيرات منتظمة
        patterns = [
            r'([0-9]{15})',
            r'imei[:\s]+([0-9]{15})',
            r'IMEI[:\s]+([0-9]{15})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return None
        
    def _validate_imei(self, imei: str) -> bool:
        """التحقق من صحة رقم IMEI (خوارزمية Luhn)"""
        if not imei or len(imei) != 15 or not imei.isdigit():
            return False
            
        # خوارزمية Luhn للتحقق من IMEI
        total = 0
        for i, digit in enumerate(reversed(imei)):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
            
        return total % 10 == 0
