import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qdarkstyle import load_stylesheet_pyqt5
from ui.widgets.device_panel import DevicePanel
from ui.widgets.log_panel import LogPanel
from ui.widgets.flash_panel import FlashPanel
from ui.widgets.backup_panel import BackupPanel
from tools.frp_unlock import FRPUnlocker
from tools.imei_tool import IMEITool
from core.device_manager import DeviceManager
from core.notification_system import NotificationSystem
from core.logger import Logger

class MainWindow(QMainWindow):
    """النافذة الرئيسية لتطبيق DeviceForge Pro"""
    
    def __init__(self):
        super().__init__()
        self.device_manager = DeviceManager()
        self.notification_system = NotificationSystem()
        self.logger = Logger()
        self.init_ui()
        self.setup_connections()
        self.scan_devices()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        self.setWindowTitle("DeviceForge Pro v2.0 - أدوات صيانة الأجهزة المتقدمة")
        self.setGeometry(100, 100, 1400, 900)
        
        # تعيين الأيقونة
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        
        # إنشاء القوائم
        self.create_menus()
        
        # إنشاء شريط الأدوات
        self.create_toolbar()
        
        # الواجهة الرئيسية
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # إنشاء التبويبات
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(False)
        
        # تبويب الأجهزة
        self.device_tab = QWidget()
        self.setup_device_tab()
        self.tab_widget.addTab(self.device_tab, "📱 الأجهزة")
        
        # تبويب الفلاش
        self.flash_tab = FlashPanel()
        self.tab_widget.addTab(self.flash_tab, "⚡ فلاش ROM")
        
        # تبويب النسخ الاحتياطي
        self.backup_tab = BackupPanel()
        self.tab_widget.addTab(self.backup_tab, "💾 نسخ احتياطي")
        
        # تبويب أدوات FRP
        self.frp_tab = QWidget()
        self.setup_frp_tab()
        self.tab_widget.addTab(self.frp_tab, "🔓 أدوات FRP")
        
        # تبويب IMEI
        self.imei_tab = QWidget()
        self.setup_imei_tab()
        self.tab_widget.addTab(self.imei_tab, "📱 أدوات IMEI")
        
        # تبويب السجلات
        self.log_tab = LogPanel()
        self.tab_widget.addTab(self.log_tab, "📋 السجلات")
        
        main_layout.addWidget(self.tab_widget)
        
        # شريط الحالة
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("جاهز للعمل - DeviceForge Pro")
        
        # تطبيق الثيم الداكن
        self.apply_dark_theme()
        
        # نظام الإشعارات
        self.notification_system.set_parent(self)
        
    def create_menus(self):
        """إنشاء القوائم الرئيسية"""
        menubar = self.menuBar()
        
        # قائمة ملف
        file_menu = menubar.addMenu("ملف")
        
        open_action = QAction("فتح ROM", self)
        open_action.triggered.connect(self.open_rom)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # قائمة أدوات
        tools_menu = menubar.addMenu("أدوات")
        
        scan_action = QAction("مسح الأجهزة", self)
        scan_action.triggered.connect(self.scan_devices)
        tools_menu.addAction(scan_action)
        
        tools_menu.addSeparator()
        
        frp_action = QAction("إزالة FRP", self)
        frp_action.triggered.connect(self.open_frp_tab)
        tools_menu.addAction(frp_action)
        
        imei_action = QAction("أداة IMEI", self)
        imei_action.triggered.connect(self.open_imei_tab)
        tools_menu.addAction(imei_action)
        
        # قائمة مساعدة
        help_menu = menubar.addMenu("مساعدة")
        
        about_action = QAction("حول البرنامج", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """إنشاء شريط الأدوات"""
        toolbar = self.addToolBar("أدوات سريعة")
        toolbar.setMovable(False)
        
        # أزرار سريعة
        scan_btn = QAction("📱 مسح", self)
        scan_btn.triggered.connect(self.scan_devices)
        toolbar.addAction(scan_btn)
        
        toolbar.addSeparator()
        
        flash_btn = QAction("⚡ فلاش", self)
        flash_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(flash_btn)
        
        backup_btn = QAction("💾 نسخ", self)
        backup_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(backup_btn)
        
        toolbar.addSeparator()
        
        frp_btn = QAction("🔓 FRP", self)
        frp_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        toolbar.addAction(frp_btn)
        
        imei_btn = QAction("📱 IMEI", self)
        imei_btn.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        toolbar.addAction(imei_btn)
        
    def setup_device_tab(self):
        """تهيئة تبويب الأجهزة"""
        layout = QVBoxLayout(self.device_tab)
        
        # لوحة الأجهزة
        self.device_panel = DevicePanel()
        layout.addWidget(self.device_panel)
        
        # معلومات الجهاز
        info_group = QGroupBox("معلومات الجهاز المختار")
        info_layout = QVBoxLayout()
        
        self.device_info_text = QTextEdit()
        self.device_info_text.setReadOnly(True)
        self.device_info_text.setMaximumHeight(150)
        info_layout.addWidget(self.device_info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # أزرار التحكم
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 تحديث المعلومات")
        refresh_btn.clicked.connect(self.refresh_device_info)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
    def setup_frp_tab(self):
        """تهيئة تبويب أدوات FRP"""
        layout = QVBoxLayout(self.frp_tab)
        
        # وصف الأداة
        desc_label = QLabel("🔓 أدوات إزالة قفل Google FRP (Factory Reset Protection)")
        desc_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(desc_label)
        
        # إطار الإعدادات
        settings_group = QGroupBox("إعدادات FRP")
        settings_layout = QGridLayout()
        
        # اختيار الجهاز
        settings_layout.addWidget(QLabel("الجهاز:"), 0, 0)
        self.frp_device_combo = QComboBox()
        self.frp_device_combo.addItem("اختر جهاز...")
        settings_layout.addWidget(self.frp_device_combo, 0, 1)
        
        # نوع FRP
        settings_layout.addWidget(QLabel("نوع الإزالة:"), 1, 0)
        self.frp_type_combo = QComboBox()
        self.frp_type_combo.addItems([
            "طريقة ADB (سريعة)",
            "طريقة EDL (متقدمة)",
            "طريقة Bootloader"
        ])
        settings_layout.addWidget(self.frp_type_combo, 1, 1)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # زر التنفيذ
        self.frp_execute_btn = QPushButton("🔓 إزالة FRP الآن")
        self.frp_execute_btn.setStyleSheet("""
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
        self.frp_execute_btn.clicked.connect(self.execute_frp)
        layout.addWidget(self.frp_execute_btn)
        
        # سجل النتائج
        self.frp_log = QTextEdit()
        self.frp_log.setReadOnly(True)
        self.frp_log.setMaximumHeight(200)
        layout.addWidget(QLabel("سجل العمليات:"))
        layout.addWidget(self.frp_log)
        
        # زر مسح السجل
        clear_btn = QPushButton("🗑️ مسح السجل")
        clear_btn.clicked.connect(lambda: self.frp_log.clear())
        layout.addWidget(clear_btn)
        
    def setup_imei_tab(self):
        """تهيئة تبويب أدوات IMEI"""
        layout = QVBoxLayout(self.imei_tab)
        
        # وصف الأداة
        desc_label = QLabel("📱 أدوات إصلاح وتغيير أرقام IMEI")
        desc_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        layout.addWidget(desc_label)
        
        # إطار الإعدادات
        settings_group = QGroupBox("إعدادات IMEI")
        settings_layout = QGridLayout()
        
        # اختيار الجهاز
        settings_layout.addWidget(QLabel("الجهاز:"), 0, 0)
        self.imei_device_combo = QComboBox()
        self.imei_device_combo.addItem("اختر جهاز...")
        settings_layout.addWidget(self.imei_device_combo, 0, 1)
        
        # شريحة IMEI
        settings_layout.addWidget(QLabel("شريحة IMEI:"), 1, 0)
        self.imei_slot_combo = QComboBox()
        self.imei_slot_combo.addItems(["IMEI 1", "IMEI 2"])
        settings_layout.addWidget(self.imei_slot_combo, 1, 1)
        
        # رقم IMEI الجديد
        settings_layout.addWidget(QLabel("IMEI الجديد:"), 2, 0)
        self.imei_new_edit = QLineEdit()
        self.imei_new_edit.setPlaceholderText("أدخل رقم IMEI مكون من 15 رقم")
        self.imei_new_edit.setMaxLength(15)
        settings_layout.addWidget(self.imei_new_edit, 2, 1)
        
        # زر قراءة IMEI الحالي
        read_imei_btn = QPushButton("📖 قراءة IMEI الحالي")
        read_imei_btn.clicked.connect(self.read_current_imei)
        settings_layout.addWidget(read_imei_btn, 3, 0)
        
        # عرض IMEI الحالي
        self.current_imei_label = QLabel("IMEI الحالي: غير معروف")
        self.current_imei_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        settings_layout.addWidget(self.current_imei_label, 3, 1)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # زر التنفيذ
        self.imei_execute_btn = QPushButton("💾 تغيير IMEI")
        self.imei_execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.imei_execute_btn.clicked.connect(self.execute_imei_change)
        layout.addWidget(self.imei_execute_btn)
        
        # سجل النتائج
        self.imei_log = QTextEdit()
        self.imei_log.setReadOnly(True)
        self.imei_log.setMaximumHeight(200)
        layout.addWidget(QLabel("سجل العمليات:"))
        layout.addWidget(self.imei_log)
        
        # زر مسح السجل
        clear_btn = QPushButton("🗑️ مسح السجل")
        clear_btn.clicked.connect(lambda: self.imei_log.clear())
        layout.addWidget(clear_btn)
        
    def setup_connections(self):
        """ربط الإشارات والمنافذ"""
        # عند تغيير التبويب
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # عند اختيار جهاز
        if hasattr(self.device_panel, 'device_selected'):
            self.device_panel.device_selected.connect(self.on_device_selected)
        
    def apply_dark_theme(self):
        """تطبيق الثيم الداكن"""
        try:
            self.setStyleSheet(load_stylesheet_pyqt5())
            # تخصيص إضافي
            custom_style = """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px 20px;
                margin: 2px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
                border-bottom: 2px solid #4CAF50;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            """
            self.setStyleSheet(self.styleSheet() + custom_style)
        except Exception as e:
            print(f"خطأ في تطبيق الثيم: {e}")
            
    def scan_devices(self):
        """مسح الأجهزة المتصلة"""
        self.status_bar.showMessage("جاري مسح الأجهزة...")
        devices = self.device_manager.scan_devices()
        
        # تحديث قوائم الأجهزة في التبويبات
        adb_devices = devices.get('adb', [])
        fastboot_devices = devices.get('fastboot', [])
        
        # تحديث قائمة FRP
        self.frp_device_combo.clear()
        self.frp_device_combo.addItem("اختر جهاز...")
        for device in adb_devices + fastboot_devices:
            if isinstance(device, dict) and 'serial' in device:
                self.frp_device_combo.addItem(device['serial'])
        
        # تحديث قائمة IMEI
        self.imei_device_combo.clear()
        self.imei_device_combo.addItem("اختر جهاز...")
        for device in adb_devices + fastboot_devices:
            if isinstance(device, dict) and 'serial' in device:
                self.imei_device_combo.addItem(device['serial'])
        
        # تحديث لوحة الأجهزة
        self.device_panel.update_devices(devices)
        
        # عرض الإشعار
        count = len(adb_devices) + len(fastboot_devices)
        self.status_bar.showMessage(f"تم العثور على {count} جهاز")
        self.notification_system.show_notification(
            "مسح الأجهزة",
            f"تم العثور على {count} جهاز متصل",
            "info"
        )
        
        self.logger.info(f"تم مسح الأجهزة - {count} جهاز")
        
    def on_device_selected(self, device_info):
        """عند اختيار جهاز"""
        self.status_bar.showMessage(f"تم اختيار الجهاز: {device_info.get('serial', 'غير معروف')}")
        self.refresh_device_info()
        
    def refresh_device_info(self):
        """تحديث معلومات الجهاز"""
        info = self.device_manager.get_device_info()
        if info:
            text = "معلومات الجهاز:\n"
            for key, value in info.items():
                if not key.startswith('_'):
                    text += f"• {key}: {value}\n"
            self.device_info_text.setText(text)
        
    def on_tab_changed(self, index):
        """عند تغيير التبويب"""
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"التبويب الحالي: {tab_name}")
        
    def open_rom(self):
        """فتح ملف ROM"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "اختر ملف ROM",
            "",
            "ROM Files (*.zip *.img *.tar *.md5);;All Files (*.*)"
        )
        if file_path:
            self.notification_system.show_notification(
                "فتح ROM",
                f"تم تحميل ROM: {os.path.basename(file_path)}",
                "success"
            )
            # إرسال إلى تبويب الفلاش
            self.flash_tab.set_rom_path(file_path)
            self.tab_widget.setCurrentIndex(1)
        
    def open_frp_tab(self):
        """فتح تبويب FRP"""
        self.tab_widget.setCurrentIndex(3)
        
    def open_imei_tab(self):
        """فتح تبويب IMEI"""
        self.tab_widget.setCurrentIndex(4)
        
    def execute_frp(self):
        """تنفيذ إزالة FRP"""
        device = self.frp_device_combo.currentText()
        frp_type = self.frp_type_combo.currentText()
        
        if device == "اختر جهاز...":
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار جهاز أولاً")
            return
            
        self.frp_execute_btn.setEnabled(False)
        self.frp_log.append(f"🔓 بدء إزالة FRP للجهاز {device} باستخدام {frp_type}...")
        
        # إنشاء كائن FRP وتنفيذ العملية في خيط منفصل
        self.frp_worker = FRPWorker(device, frp_type)
        self.frp_worker.progress.connect(self.update_frp_progress)
        self.frp_worker.finished.connect(self.frp_finished)
        self.frp_worker.start()
        
    def update_frp_progress(self, message):
        """تحديث تقدم FRP"""
        self.frp_log.append(f"📌 {message}")
        self.status_bar.showMessage(message)
        
    def frp_finished(self, result):
        """اكتمال عملية FRP"""
        self.frp_execute_btn.setEnabled(True)
        if result.get('success'):
            self.frp_log.append("✅ تم إزالة FRP بنجاح!")
            self.notification_system.show_notification(
                "إزالة FRP",
                "تم إزالة قفل Google FRP بنجاح",
                "success"
            )
        else:
            self.frp_log.append(f"❌ فشل إزالة FRP: {result.get('error', 'خطأ غير معروف')}")
            self.notification_system.show_notification(
                "إزالة FRP",
                "فشل إزالة قفل FRP",
                "error"
            )
            
    def read_current_imei(self):
        """قراءة IMEI الحالي"""
        device = self.imei_device_combo.currentText()
        if device == "اختر جهاز...":
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار جهاز أولاً")
            return
            
        # محاكاة قراءة IMEI (سيتم تطويرها لاحقاً)
        import random
        imei = ''.join([str(random.randint(0, 9)) for _ in range(15)])
        self.current_imei_label.setText(f"IMEI الحالي: {imei}")
        self.imei_log.append(f"📖 قراءة IMEI الحالي: {imei}")
        
    def execute_imei_change(self):
        """تغيير IMEI"""
        device = self.imei_device_combo.currentText()
        new_imei = self.imei_new_edit.text().strip()
        slot = self.imei_slot_combo.currentText()
        
        if device == "اختر جهاز...":
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار جهاز أولاً")
            return
            
        if len(new_imei) != 15 or not new_imei.isdigit():
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال رقم IMEI صحيح مكون من 15 رقم")
            return
            
        self.imei_execute_btn.setEnabled(False)
        self.imei_log.append(f"💾 بدأ تغيير IMEI للجهاز {device} - الشريحة {slot}")
        self.imei_log.append(f"📱 IMEI الجديد: {new_imei}")
        
        # محاكاة تغيير IMEI
        self.imei_worker = IMEIWorker(device, new_imei, slot)
        self.imei_worker.progress.connect(self.update_imei_progress)
        self.imei_worker.finished.connect(self.imei_finished)
        self.imei_worker.start()
        
    def update_imei_progress(self, message):
        """تحديث تقدم IMEI"""
        self.imei_log.append(f"📌 {message}")
        self.status_bar.showMessage(message)
        
    def imei_finished(self, result):
        """اكتمال تغيير IMEI"""
        self.imei_execute_btn.setEnabled(True)
        if result.get('success'):
            self.imei_log.append("✅ تم تغيير IMEI بنجاح!")
            self.current_imei_label.setText(f"IMEI الجديد: {self.imei_new_edit.text()}")
            self.notification_system.show_notification(
                "تغيير IMEI",
                "تم تغيير رقم IMEI بنجاح",
                "success"
            )
        else:
            self.imei_log.append(f"❌ فشل تغيير IMEI: {result.get('error', 'خطأ غير معروف')}")
            self.notification_system.show_notification(
                "تغيير IMEI",
                "فشل تغيير رقم IMEI",
                "error"
            )
            
    def show_about(self):
        """عرض معلومات عن البرنامج"""
        QMessageBox.about(
            self,
            "حول DeviceForge Pro",
            """
            <h2>DeviceForge Pro v2.0</h2>
            <p>أداة متقدمة لصيانة الأجهزة المحمولة</p>
            <p><b>الميزات:</b></p>
            <ul>
                <li>فلاش ROMs بسهولة</li>
                <li>نسخ احتياطي واستعادة</li>
                <li>إزالة قفل FRP</li>
                <li>تغيير وإصلاح IMEI</li>
                <li>دعم أجهزة متعددة</li>
            </ul>
            <p><b>الإصدار:</b> 2.0.0</p>
            <p><b>المطور:</b> DeviceForge Team</p>
            """
        )

class FRPWorker(QThread):
    """خيط عمل لإزالة FRP"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, device, frp_type):
        super().__init__()
        self.device = device
        self.frp_type = frp_type
        
    def run(self):
        """تنفيذ عملية FRP"""
        try:
            frp = FRPUnlocker()
            
            # تحديد نوع FRP
            if "ADB" in self.frp_type:
                result = frp.remove_frp_adb(self.device)
            elif "EDL" in self.frp_type:
                result = frp.remove_frp_edl(self.device)
            else:
                result = frp.remove_frp_bootloader(self.device)
            
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})

class IMEIWorker(QThread):
    """خيط عمل لتغيير IMEI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, device, new_imei, slot):
        super().__init__()
        self.device = device
        self.new_imei = new_imei
        self.slot = slot
        
    def run(self):
        """تنفيذ تغيير IMEI"""
        try:
            imei_tool = IMEITool()
            result = imei_tool.change_imei(self.device, self.new_imei, self.slot)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})
# أضف في create_menus()
def create_menus(self):
    # ... الكود السابق ...
    
    # قائمة مساعدة
    help_menu = menubar.addMenu("مساعدة")
    
    # أضف هذا الخيار
    interactive_help_action = QAction("🎯 المساعدة التفاعلية", self)
    interactive_help_action.triggered.connect(self.show_interactive_help)
    help_menu.addAction(interactive_help_action)
    
    help_menu.addSeparator()
    
    about_action = QAction("حول البرنامج", self)
    about_action.triggered.connect(self.show_about)
    help_menu.addAction(about_action)

# أضف هذه الدالة
def show_interactive_help(self):
    """عرض المساعدة التفاعلية"""
    if hasattr(self, 'help_panel') and self.help_panel:
        self.help_panel.show()
        self.tab_widget.setCurrentIndex(self.tab_widget.indexOf(self.help_panel))
    else:
        from ui.widgets.help_panel import HelpPanel
        self.help_panel = HelpPanel()
        self.tab_widget.addTab(self.help_panel, "🎯 المساعدة")
        self.tab_widget.setCurrentIndex(self.tab_widget.indexOf(self.help_panel))

# أضف في init_ui() بعد إنشاء التبويبات
# تبويب المساعدة
self.help_tab = HelpPanel()
self.tab_widget.addTab(self.help_tab, "🎯 المساعدة")
