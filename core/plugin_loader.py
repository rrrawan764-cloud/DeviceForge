import os
import sys
import importlib
import inspect
from typing import Dict, List, Any
from pathlib import Path
from core.logger import Logger

class PluginLoader:
    """نظام تحميل وإدارة الإضافات"""
    
    def __init__(self):
        self.logger = Logger()
        self.plugins = {}
        self.plugin_dir = "plugins/"
        self.loaded_plugins = []
        
    def load_plugins(self) -> Dict:
        """تحميل جميع الإضافات من مجلد plugins"""
        self.logger.info("بدء تحميل الإضافات...")
        
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            self.logger.info("تم إنشاء مجلد plugins")
        
        # مسح مجلد الإضافات
        plugin_files = Path(self.plugin_dir).glob("*.py")
        
        for plugin_file in plugin_files:
            try:
                plugin_name = plugin_file.stem
                if plugin_name.startswith('_'):
                    continue
                    
                # تحميل الوحدة
                spec = importlib.util.spec_from_file_location(
                    plugin_name, 
                    str(plugin_file)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # البحث عن فئة الإضافة
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, 'plugin_info'):
                        plugin_instance = obj()
                        self.plugins[plugin_name] = plugin_instance
                        self.loaded_plugins.append(plugin_name)
                        
                        self.logger.info(f"تم تحميل الإضافة: {plugin_name}")
                        
                        # تنفيذ دالة التهيئة إن وجدت
                        if hasattr(plugin_instance, 'initialize'):
                            plugin_instance.initialize()
                            
            except Exception as e:
                self.logger.error(f"خطأ في تحميل الإضافة {plugin_file}: {e}")
        
        return self.plugins
    
    def get_plugin(self, plugin_name: str) -> Any:
        """الحصول على إضافة معينة"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[str]:
        """الحصول على قائمة جميع الإضافات"""
        return self.loaded_plugins
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """تفعيل إضافة"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, 'enable'):
                plugin.enable()
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """تعطيل إضافة"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, 'disable'):
                plugin.disable()
            return True
        return False
    
    def reload_plugins(self) -> Dict:
        """إعادة تحميل جميع الإضافات"""
        self.plugins.clear()
        self.loaded_plugins.clear()
        return self.load_plugins()

# مثال لإضافة نموذجية
class SamplePlugin:
    """نموذج لإضافة بسيطة"""
    
    def __init__(self):
        self.name = "Sample Plugin"
        self.version = "1.0.0"
        self.author = "DeviceForge Team"
        self.enabled = False
    
    @staticmethod
    def plugin_info():
        return {
            'name': 'Sample Plugin',
            'version': '1.0.0',
            'author': 'DeviceForge Team',
            'description': 'هذا إضافة نموذجية'
        }
    
    def initialize(self):
        """تهيئة الإضافة"""
        print(f"تم تهيئة {self.name}")
    
    def enable(self):
        """تفعيل الإضافة"""
        self.enabled = True
        print(f"تم تفعيل {self.name}")
    
    def disable(self):
        """تعطيل الإضافة"""
        self.enabled = False
        print(f"تم تعطيل {self.name}")
    
    def execute(self, *args, **kwargs):
        """تنفيذ وظيفة الإضافة"""
        if self.enabled:
            return f"تم تنفيذ {self.name}"
        return "الإضافة غير مفعلة"
