from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import os

class HelpPanel(QWidget):
    """لوحة المساعدة التفاعلية للمستخدمين الجدد"""
    
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.help_data = self.load_help_data()
        self.init_ui()
        
    def load_help_data(self) -> dict:
        """تحميل بيانات المساعدة"""
        # بيانات المساعدة المدمجة
        help_data = {
            'steps': [
                {
                    'title': '📱 مرحباً بك في DeviceForge Pro',
                    'content': 'أداة متقدمة لصيانة الأجهزة المحمولة\n\n'
                              'سنساعدك خطوة بخطوة لتعلم استخدام البرنامج',
                    'icon': '🚀'
                },
                {
                    'title': '🔌 توصيل الجهاز',
                    'content': '• قم بتوصيل جهازك عبر USB\n'
                              '• تأكد من تفعيل وضع المطور (Developer Options)\n'
                              '• فعّل تصحيح USB (USB Debugging)\n\n'
                              '📌 اضغط على "مسح الأجهزة" للكشف عنه',
                    'icon': '📱'
                },
                {
                    'title': '⚡ فلاش ROM',
                    'content': '1. اسحب ملف ROM إلى المنطقة المحددة\n'
                              '2. اختر الجهاز من القائمة\n'
                              '3. اختر نوع الفلاش (Fastboot/ADB/EDL)\n'
                              '4. اضغط "بدء الفلاش"\n\n'
                              '⚠️ تأكد من اختيار ROM المناسب لجهازك',
                    'icon': '💾'
                },
                {
                    'title': '💾 النسخ الاحتياطي',
                    'content': '• اختر نوع النسخ (كامل/تطبيقات/جهات اتصال)\n'
                              '• اضغط "بدء النسخ"\n'
                              '• سيتم حفظ النسخ في مجلد backups/\n\n'
                              '📌 يمكنك استعادة النسخ في أي وقت',
                    'icon': '💿'
                },
                {
                    'title': '🔓 أدوات FRP',
                    'content': 'لإزالة قفل Google FRP:\n'
                              '1. اختر جهازك المتصل\n'
                              '2. اختر نوع الإزالة (ADB/EDL/Bootloader)\n'
                              '3. اضغط "إزالة FRP الآن"\n\n'
                              '⚠️ قد تحتاج إلى إعادة تشغيل الجهاز',
                    'icon': '🔑'
                },
                {
                    'title': '📱 أدوات IMEI',
                    'content': 'لتغيير أو إصلاح IMEI:\n'
                              '1. اختر جهازك\n'
                              '2. اختر الشريحة (IMEI 1/IMEI 2)\n'
                              '3. أدخل IMEI الجديد (15 رقم)\n'
                              '4. اضغط "تغيير IMEI"\n\n'
                              '⚠️ استخدم بحذر! تغيير IMEI غير قانوني في بعض الدول',
                    'icon': '📋'
                },
                {
                    'title': '🎯 نصائح مهمة',
                    'content': '• تأكد من شحن البطارية 50%+ قبل الفلاش\n'
                              '• استخدم كابل USB أصلي\n'
                              '• احتفظ بنسخة احتياطية من بياناتك\n'
                              '• اقرأ التعليمات قبل تنفيذ أي عملية\n\n'
                              '💡 يمكنك دائماً العودة لهذه المساعدة',
                    'icon': '💡'
                }
            ]
        }
        return help_data
    
    def init_ui(self):
        """تهيئة واجهة المساعدة"""
        layout = QVBoxLayout()
        
        # منطقة العرض
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(self.help_data['steps']) - 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v من %m")
        layout.addWidget(self.progress_bar)
        
        # عرض الخطوة الحالية
        self.step_widget = QWidget()
        self.step_layout = QVBoxLayout(self.step_widget)
        self.step_layout.setContentsMargins(20, 20, 20, 20)
        
        # تنسيق الخلفية
        self.step_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        layout.addWidget(self.step_widget)
        
        # أزرار التنقل
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("⬅ السابق")
        self.prev_btn.clicked.connect(self.prev_step)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)
        
        nav_layout.addStretch()
        
        self.next_btn = QPushButton("التالي ➡")
        self.next_btn.clicked.connect(self.next_step)
        nav_layout.addWidget(self.next_btn)
        
        # زر إعادة تعيين المساعدة
        reset_btn = QPushButton("🔄 إعادة تعيين")
        reset_btn.clicked.connect(self.reset_help)
        nav_layout.addWidget(reset_btn)
        
        layout.addLayout(nav_layout)
        
        # زر إغلاق المساعدة
        close_btn = QPushButton("❌ إغلاق المساعدة")
        close_btn.clicked.connect(self.hide_help)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # عرض الخطوة الأولى
        self.show_step(0)
        
    def show_step(self, index: int):
        """عرض خطوة معينة"""
        if 0 <= index < len(self.help_data['steps']):
            step = self.help_data['steps'][index]
            
            # مسح المحتوى القديم
            while self.step_layout.count():
                item = self.step_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # إضافة الأيقونة والعنوان
            title_label = QLabel(f"{step['icon']} {step['title']}")
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                padding-bottom: 10px;
            """)
            self.step_layout.addWidget(title_label)
            
            # إضافة المحتوى
            content_label = QLabel(step['content'])
            content_label.setStyleSheet("""
                font-size: 14px;
                padding: 10px;
                line-height: 1.6;
            """)
            content_label.setWordWrap(True)
            self.step_layout.addWidget(content_label)
            
            # إضافة مساحة لبعض الأزرار التفاعلية في الخطوات المناسبة
            if index == 1:  # خطوة توصيل الجهاز
                scan_btn = QPushButton("📱 مسح الأجهزة الآن")
                scan_btn.clicked.connect(self.scan_devices)
                self.step_layout.addWidget(scan_btn)
            elif index == 2:  # خطوة فلاش ROM
                open_btn = QPushButton("📂 فتح ROM")
                open_btn.clicked.connect(self.open_rom)
                self.step_layout.addWidget(open_btn)
            
            self.step_layout.addStretch()
            
            # تحديث شريط التقدم
            self.progress_bar.setValue(index)
            self.current_step = index
            
            # تحديث حالة الأزرار
            self.prev_btn.setEnabled(index > 0)
            self.next_btn.setText("إنهاء" if index == len(self.help_data['steps']) - 1 else "التالي ➡")
    
    def next_step(self):
        """الانتقال إلى الخطوة التالية"""
        if self.current_step < len(self.help_data['steps']) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.hide_help()
    
    def prev_step(self):
        """الانتقال إلى الخطوة السابقة"""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def reset_help(self):
        """إعادة تعيين المساعدة للبداية"""
        self.show_step(0)
        
    def hide_help(self):
        """إخفاء المساعدة"""
        self.parent().tab_widget.setCurrentIndex(0)
        QMessageBox.information(
            self,
            "تم إنهاء المساعدة",
            "🎉 يمكنك العودة للمساعدة في أي وقت\n"
            "من قائمة Help > المساعدة التفاعلية"
        )
    
    def scan_devices(self):
        """مسح الأجهزة (متصل بالنافذة الرئيسية)"""
        if hasattr(self.parent(), 'scan_devices'):
            self.parent().scan_devices()
    
    def open_rom(self):
        """فتح ROM (متصل بالنافذة الرئيسية)"""
        if hasattr(self.parent(), 'open_rom'):
            self.parent().open_rom()
