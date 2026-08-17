#!/usr/bin/env python3
"""
DeviceForge Pro - أداة متقدمة لصيانة الأجهزة المحمولة
الإصدار: 2.0.0
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from core.logger import Logger

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    # تهيئة السجلات
    logger = Logger()
    logger.info("بدء تشغيل DeviceForge Pro v2.0")
    
    # إنشاء مجلدات ضرورية
    os.makedirs("logs", exist_ok=True)
    os.makedirs("assets/icons", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # تشغيل التطبيق
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
