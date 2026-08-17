from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time

class NotificationSystem(QObject):
    """نظام الإشعارات المتقدم للواجهة الرسومية"""
    
    notification_shown = pyqtSignal(str, str, str)  # title, message, type
    
    def __init__(self):
        super().__init__()
        self.parent = None
        self.notifications = []
        self.max_notifications = 5
        
    def set_parent(self, parent):
        """تعيين النافذة الأب"""
        self.parent = parent
        
    def show_notification(self, title, message, notif_type="info", duration=3000):
        """عرض إشعار"""
        if not self.parent:
            print(f"📢 {title}: {message}")
            return
            
        # إنشاء إشعار عائم
        notification = FloatingNotification(title, message, notif_type, duration)
        notification.show()
        
        # إرسال الإشارة
        self.notification_shown.emit(title, message, notif_type)
        
        # إضافة للسجل
        self.notifications.append({
            'title': title,
            'message': message,
            'type': notif_type,
            'time': time.time()
        })
        
        # الحد من عدد الإشعارات
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
            
    def clear_notifications(self):
        """مسح جميع الإشعارات"""
        self.notifications.clear()
        
    def get_notifications(self):
        """الحصول على قائمة الإشعارات"""
        return self.notifications.copy()

class FloatingNotification(QWidget):
    """إشعار عائم يظهر فوق الواجهة"""
    
    def __init__(self, title, message, notif_type="info", duration=3000):
        super().__init__()
        self.title = title
        self.message = message
        self.notif_type = notif_type
        self.duration = duration
        self.init_ui()
        self.animation = None
        
    def init_ui(self):
        """تهيئة واجهة الإشعار"""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # تحديد الألوان حسب النوع
        colors = {
            "info": ("#2196F3", "#BBDEFB"),
            "success": ("#4CAF50", "#C8E6C9"),
            "warning": ("#FF9800", "#FFE0B2"),
            "error": ("#F44336", "#FFCDD2")
        }
        
        bg_color, border_color = colors.get(self.notif_type, colors["info"])
        
        # إنشاء المحتوى
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        
        # العنوان
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            color: {bg_color};
            font-size: 14px;
            font-weight: bold;
        """)
        main_layout.addWidget(title_label)
        
        # الرسالة
        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("color: #333333; font-size: 12px;")
        msg_label.setWordWrap(True)
        main_layout.addWidget(msg_label)
        
        # زر الإغلاق
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #000000;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        # تخطيط رئيسي مع زر الإغلاق
        container = QWidget()
        container.setStyleSheet(f"""
            background-color: #ffffff;
            border: 2px solid {bg_color};
            border-radius: 8px;
            padding: 5px;
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        container_layout.addLayout(header_layout)
        container_layout.addWidget(msg_label)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # تحديد الموقع (أسفل يمين الشاشة)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.setGeometry(
            screen_geometry.width() - 400,
            screen_geometry.height() - 200,
            350,
            100
        )
        
        # بدء المؤقت للإغلاق التلقائي
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.fade_out)
            
        # تأثير الظهور
        self.show_animation()
        
    def show_animation(self):
        """تأثير ظهور الإشعار"""
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        
    def fade_out(self):
        """تأثير اختفاء الإشعار"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close)
        self.animation.start()
