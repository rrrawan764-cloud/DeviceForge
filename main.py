k#!/usr/bin/env python3
"""
DeviceForge Pro v2.1 - أداة متقدمة لصيانة الأجهزة المحمولة
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from core.logger import Logger
from core.plugin_loader import PluginLoader
from core.updater import Updater

def main():
    """الدالة الرئيسية"""
    logger = Logger()
    logger.info("بدء تشغيل DeviceForge Pro v2.1")
    
    # إنشاء المجلدات الضرورية
    os.makedirs("logs", exist_ok=True)
    os.makedirs("assets/icons", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("plugins", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # تهيئة التطبيق
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # شاشة الترحيب
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(Qt.darkGray)
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    splash.showMessage("🚀 جاري تحميل DeviceForge Pro...", Qt.AlignCenter, Qt.white)
    QApplication.processEvents()
    
    # تحميل الإضافات
    splash.showMessage("📦 تحميل الإضافات...", Qt.AlignCenter, Qt.white)
    plugin_loader = PluginLoader()
    plugins = plugin_loader.load_plugins()
    
    # التحقق من التحديثات (في الخلفية)
    splash.showMessage("🔄 التحقق من التحديثات...", Qt.AlignCenter, Qt.white)
    updater = Updater()
    update_info = updater.check_for_updates()
    
    # فتح النافذة الرئيسية
    from ui.main_window import MainWindow
    window = MainWindow()
    
    # عرض معلومات التحديث إن وجدت
    if update_info.get('available'):
        QTimer.singleShot(2000, lambda: show_update_notification(window, update_info))
    
    splash.finish(window)
    window.show()
    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)

def show_update_notification(window, update_info):
    """عرض إشعار التحديث"""
    from PyQt5.QtWidgets import QMessageBox
    
    changelog = "\n".join([f"• {change}" for change in update_info.get('changelog', [])])
    reply = QMessageBox.question(
        window,
        "🔄 تحديث متاح",
        f"يتوفر إصدار جديد: {update_info.get('version')}\n\n"
        f"التغييرات:\n{changelog}\n\n"
        f"حجم التحديث: {update_info.get('size', 'غير معروف')}\n\n"
        "هل تريد تحميل التحديث الآن؟",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        # بدء تحميل التحديث
        QMessageBox.information(
            window,
            "تحميل التحديث",
            "جاري تحميل التحديث...\n"
            "سيتم إعادة تشغيل التطبيق بعد التثبيت"
        )

if __name__ == "__main__":
    main()
