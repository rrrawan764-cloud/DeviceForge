
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from tools.flash_tool import FlashTool
from core.device_manager import DeviceManager
from core.notification_system import NotificationSystem
import os

class FlashPanel(QWidget):
    """لوحة الفلاش مع دعم السحب والإفلات"""
    
    def __init__(self):
        super().__init__()
        self.flash_tool = FlashTool()
        self.device_manager = DeviceManager()
        self.notification_system = NotificationSystem()
        self.rom_path = None
        self.init_ui()
        self.setAcceptDrops(True)  # تفعيل السحب والإفلات
        
    def init_ui(self):
        """تهيئة واجهة الفلاش"""
        layout = QVBoxLayout()
        
        # منطقة السحب والإفلات
        self.drop_area = QLabel()
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setMinimumHeight(150)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #4CAF50;
                border-radius: 10px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 16px;
            }
            QLabel:hover {
                background-color: #3d3d3d;
                border-color: #66BB6A;
            }
        """)
        self.drop_area.setText(
            "📂 اسحب ملف ROM هنا\n"
            "أو اضغط للاختيار\n\n"
            "مدعوم: .zip, .img, .tar, .md5"
        )
        self.drop_area.mousePressEvent = self.on_drop_area_click
        layout.addWidget(self.drop_area)
        
        # معلومات ROM
        self.rom_info_label = QLabel("لم يتم اختيار ROM")
        self.rom_info_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        layout.addWidget(self.rom_info_label)
        
        # إعدادات الفلاش
        settings_group = QGroupBox("إعدادات الفلاش")
        settings_layout = QGridLayout()
        
        # اختيار الجهاز
        settings_layout.addWidget(QLabel("الجهاز:"), 0, 0)
        self.device_combo = QComboBox()
        self.device_combo.addItem("اختر جهاز...")
        settings_layout.addWidget(self.device_combo, 0, 1)
        
        # نوع الفلاش
        settings_layout.addWidget(QLabel("نوع الفلاش:"), 1, 0)
        self.flash_type_combo = QComboBox()
        self.flash_type_combo.addItems(["Fastboot", "ADB", "EDL"])
        settings_layout.addWidget(self.flash_type_combo, 1, 1)
        
        # خيارات إضافية
        self.wipe_data_check = QCheckBox("مسح البيانات")
        self.wipe_data_check.setChecked(True)
        settings_layout.addWidget(self.wipe_data_check, 2, 0)
        
        self.wipe_cache_check = QCheckBox("مسح الكاش")
        self.wipe_cache_check.setChecked(True)
        settings_layout.addWidget(self.wipe_cache_check, 2, 1)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # زر الفلاش
        self.flash_btn = QPushButton("⚡ بدء الفلاش")
        self.flash_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.flash_btn.clicked.connect(self.start_flash)
        self.flash_btn.setEnabled(False)
        layout.addWidget(self.flash_btn)
        
        # سجل الفلاش
        layout.addWidget(QLabel("سجل الفلاش:"))
        self.flash_log = QTextEdit()
        self.flash_log.setReadOnly(True)
        self.flash_log.setMaximumHeight(200)
        layout.addWidget(self.flash_log)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        # تحديث قائمة الأجهزة
        self.update_devices()
        
    def dragEnterEvent(self, event):
        """عند سحب ملف إلى المنطقة"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 2px solid #66BB6A;
                    border-radius: 10px;
                    background-color: #3d3d3d;
                    color: #e0e0e0;
                    font-size: 16px;
                }
            """)
            
    def dragLeaveEvent(self, event):
        """عند مغادرة الملف للمنطقة"""
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #4CAF50;
                border-radius: 10px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 16px;
            }
        """)
        
    def dropEvent(self, event):
        """عند إفلات الملف في المنطقة"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_rom(file_path)
            
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #4CAF50;
                border-radius: 10px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-size: 16px;
            }
        """)
        
    def on_drop_area_click(self, event):
        """عند النقر على منطقة السحب والإفلات"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختر ملف ROM",
            "",
            "ROM Files (*.zip *.img *.tar *.md5);;All Files (*.*)"
        )
        if file_path:
            self.load_rom(file_path)
            
    def load_rom(self, file_path):
        """تحميل ملف ROM"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "خطأ", "الملف غير موجود")
            return
            
        self.rom_path = file_path
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        self.rom_info_label.setText(
            f"📦 ROM: {file_name}\n"
            f"📊 الحجم: {file_size:.2f} MB"
        )
        
        self.flash_btn.setEnabled(True)
        self.flash_log.append(f"✅ تم تحميل ROM: {file_name}")
        self.flash_log.append(f"📊 الحجم: {file_size:.2f} MB")
        
        # عرض إشعار
        self.notification_system.show_notification(
            "تحميل ROM",
            f"تم تحميل ROM: {file_name}",
            "success"
        )
        
    def set_rom_path(self, path):
        """تعيين مسار ROM (من القوائم)"""
        self.load_rom(path)
        
    def update_devices(self):
        """تحديث قائمة الأجهزة"""
        devices = self.device_manager.scan_devices()
        self.device_combo.clear()
        self.device_combo.addItem("اختر جهاز...")
        
        all_devices = devices.get('adb', []) + devices.get('fastboot', [])
        for device in all_devices:
            if isinstance(device, dict) and 'serial' in device:
                self.device_combo.addItem(device['serial'])
                
    def start_flash(self):
        """بدء عملية الفلاش"""
        device = self.device_combo.currentText()
        flash_type = self.flash_type_combo.currentText().lower()
        
        if device == "اختر جهاز...":
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار جهاز أولاً")
            return
            
        if not self.rom_path:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار ROM أولاً")
            return
            
        # تأكيد العملية
        reply = QMessageBox.question(
            self,
            "تأكيد الفلاش",
            f"هل أنت متأكد من فلاش ROM على الجهاز {device}؟\n"
            f"نوع الفلاش: {flash_type.upper()}\n"
            f"مسح البيانات: {'نعم' if self.wipe_data_check.isChecked() else 'لا'}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        self.flash_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.flash_log.append(f"⚡ بدء الفلاش للجهاز {device}...")
        
        # تنفيذ الفلاش في خيط منفصل
        self.flash_worker = FlashWorker(device, self.rom_path, flash_type)
        self.flash_worker.progress.connect(self.update_flash_progress)
        self.flash_worker.finished.connect(self.flash_finished)
        self.flash_worker.start()
        
    def update_flash_progress(self, message):
        """تحديث تقدم الفلاش"""
        self.flash_log.append(f"📌 {message}")
        
    def flash_finished(self, result):
        """اكتمال عملية الفلاش"""
        self.flash_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if result.get('status') == 'success':
            self.flash_log.append("✅ تم فلاش ROM بنجاح!")
            self.notification_system.show_notification(
                "فلاش ROM",
                "تم فلاش ROM بنجاح على الجهاز",
                "success"
            )
        else:
            error = result.get('message', 'خطأ غير معروف')
            self.flash_log.append(f"❌ فشل الفلاش: {error}")
            self.notification_system.show_notification(
                "فلاش ROM",
                f"فشل فلاش ROM: {error}",
                "error"
            )

class FlashWorker(QThread):
    """خيط عمل لعملية الفلاش"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, device, rom_path, flash_type):
        super().__init__()
        self.device = device
        self.rom_path = rom_path
        self.flash_type = flash_type
        
    def run(self):
        """تنفيذ الفلاش"""
        flash_tool = FlashTool()
        
        if self.flash_type == "fastboot":
            result = flash_tool.flash_rom(self.device, self.rom_path, 'fastboot')
        elif self.flash_type == "edl":
            result = flash_tool.flash_rom(self.device, self.rom_path, 'edl')
        else:
            result = {'status': 'error', 'message': 'نوع الفلاش غير مدعوم'}
            
        self.finished.emit(result)
