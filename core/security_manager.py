import hashlib
import json
import os
from typing import Dict, Optional
from datetime import datetime
from core.logger import Logger
from PyQt5.QtWidgets import QMessageBox, QInputDialog

class SecurityManager:
    """مدير الأمان البيومتري (بصمة، وجه، PIN)"""
    
    def __init__(self):
        self.logger = Logger()
        self.security_file = "config/security.json"
        self.auth_method = None
        self.is_authenticated = False
        
    def setup_security(self, method: str) -> Dict:
        """إعداد نظام الأمان"""
        try:
            self.logger.info(f"إعداد الأمان بطريقة: {method}")
            
            security_data = {}
            
            if method == "pin":
                # إعداد PIN
                pin, ok = QInputDialog.getText(
                    None,
                    "إعداد PIN",
                    "أدخل رقم PIN (4-6 أرقام):",
                    QInputDialog.Password
                )
                if ok and pin:
                    # تشفير PIN
                    hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
                    security_data['pin'] = hashed_pin
                    self.auth_method = 'pin'
            elif method == "fingerprint":
                # محاكاة إعداد البصمة
                QMessageBox.information(
                    None,
                    "إعداد البصمة",
                    "🔐 يرجى وضع إصبعك على ماسح البصمة\n"
                    "سيتم فتح نافذة إعداد بصمة النظام"
                )
                security_data['fingerprint'] = 'enabled'
                self.auth_method = 'fingerprint'
            elif method == "face":
                # محاكاة إعداد الوجه
                QMessageBox.information(
                    None,
                    "إعداد الوجه",
                    "👤 يرجى النظر إلى الكاميرا\n"
                    "سيتم فتح نافذة إعداد Face ID"
                )
                security_data['face'] = 'enabled'
                self.auth_method = 'face'
            
            # حفظ الإعدادات
            os.makedirs(os.path.dirname(self.security_file), exist_ok=True)
            with open(self.security_file, 'w') as f:
                json.dump(security_data, f, indent=2)
            
            return {'success': True, 'method': method}
            
        except Exception as e:
            self.logger.error(f"خطأ في إعداد الأمان: {e}")
            return {'success': False, 'error': str(e)}
    
    def authenticate(self) -> bool:
        """المصادقة باستخدام الطريقة المحددة"""
        try:
            if not os.path.exists(self.security_file):
                self.logger.info("لم يتم إعداد الأمان")
                self.is_authenticated = True
                return True
            
            with open(self.security_file, 'r') as f:
                security_data = json.load(f)
            
            if 'pin' in security_data:
                # مصادقة PIN
                pin, ok = QInputDialog.getText(
                    None,
                    "المصادقة",
                    "أدخل رقم PIN:",
                    QInputDialog.Password
                )
                if ok and pin:
                    hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
                    if hashed_pin == security_data['pin']:
                        self.is_authenticated = True
                        return True
                    else:
                        QMessageBox.warning(None, "خطأ", "PIN غير صحيح")
                        return False
                        
            elif 'fingerprint' in security_data:
                # محاكاة مصادقة البصمة
                reply = QMessageBox.question(
                    None,
                    "المصادقة البيومترية",
                    "🔐 يرجى وضع إصبعك على ماسح البصمة\n"
                    "هل تريد المتابعة؟",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.is_authenticated = True
                    return True
                return False
                
            elif 'face' in security_data:
                # محاكاة مصادقة الوجه
                reply = QMessageBox.question(
                    None,
                    "المصادقة البيومترية",
                    "👤 يرجى النظر إلى الكاميرا\n"
                    "هل تريد المتابعة؟",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.is_authenticated = True
                    return True
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في المصادقة: {e}")
            return False
    
    def require_authentication(func):
        """مزخرف للدوال التي تتطلب مصادقة"""
        def wrapper(self, *args, **kwargs):
            if not self.is_authenticated:
                if self.authenticate():
                    return func(self, *args, **kwargs)
                else:
                    QMessageBox.warning(None, "خطأ", "يجب المصادقة أولاً")
                    return None
            return func(self, *args, **kwargs)
        return wrapper
    
    def reset_security(self) -> Dict:
        """إعادة تعيين إعدادات الأمان"""
        try:
            if os.path.exists(self.security_file):
                os.remove(self.security_file)
                self.is_authenticated = False
                self.auth_method = None
                return {'success': True, 'message': 'تم إعادة تعيين الأمان'}
            return {'success': False, 'message': 'لا توجد إعدادات أمان'}
        except Exception as e:
            self.logger.error(f"خطأ في إعادة تعيين الأمان: {e}")
            return {'success': False, 'error': str(e)}
