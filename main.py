import sys
import os
import json
import random
import logging
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                            QLabel, QMessageBox, QSystemTrayIcon, QMenu, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from utils.database import get_names, record_called_name
from setting import SettingsWindow
import ctypes
# 配置日志
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_path)
logger = logging.getLogger(__name__)

class MainWindow(QWidget):
    names_updated = pyqtSignal()  # 名单更新信号
    
    def __init__(self):
        super().__init__()
        self.simple_window = None
        self.change_window = None
        self.settings_window = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_roll)
        self.is_rolling = False
        self.roll_interval = 50
        self.remaining_names = []
        
        # 初始化配置和UI
        self.config = self.load_config()
        self.init_ui()
        self.init_tray_icon()
        self.apply_theme()
        
        # 检查数据库
        self.check_database()
        
        logger.info("应用程序初始化完成")

    def check_database(self):
        """检查数据库是否可用"""
        try:
            names = get_names()
            logger.info(f"数据库检查成功，当前有 {len(names)} 个姓名")
        except Exception as e:
            logger.error(f"数据库检查失败: {e}")
            QMessageBox.critical(
                self, 
                "数据库错误",
                f"无法访问数据库:\n{str(e)}\n\n请检查应用程序是否有写入权限。"
            )

    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        default_config = {
            "theme": {"main": "light", "simple": "dark", "style": "classic"},
            "simple_mode": {"width": 320, "height": 220, "opacity": 200, "bg_color": "#ffffff"},
            "random": {"min_speed": 50, "max_speed": 200, "duration": 3000}
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("配置文件加载成功")
                    return config
            # 创建默认配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            logger.info("创建默认配置文件")
            return default_config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            QMessageBox.warning(self, "配置错误", f"加载设置失败:\n{str(e)}")
            return default_config

    def update_roll(self):
        """更新点名滚动效果"""
        try:
            if not self.remaining_names:
                self.remaining_names = get_names().copy()
                random.shuffle(self.remaining_names)
                logger.debug("重新加载名单")
            
            if not self.remaining_names:
                self.toggle_roll()
                return
                
            selected_name = random.choice(self.remaining_names)
            self.result_label.setText(selected_name)
            self.remaining_names.remove(selected_name)
            
            # 减慢速度
            max_speed = self.config["random"].get("max_speed", 200)
            self.roll_interval = min(self.roll_interval + 10, max_speed)
            self.timer.setInterval(self.roll_interval)
            
            if self.roll_interval >= max_speed:
                record_called_name(selected_name)
                self.toggle_roll()
        except Exception as e:
            logger.error(f"点名过程中出错: {e}")
            self.toggle_roll()
            QMessageBox.warning(self, "错误", f"点名过程中出错:\n{str(e)}")

    def init_ui(self):
        self.setWindowTitle('随机点名系统')
        self.resize(400, 450)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("主点名界面")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # 点名结果显示区域
        self.result_label = QLabel("点击开始点名")
        self.result_label.setObjectName("result_label")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        layout.addWidget(self.result_label)
        
        # 点名控制按钮
        roll_btn_layout = QHBoxLayout()
        self.roll_btn = QPushButton("开始点名")
        self.roll_btn.setObjectName("roll_btn")
        self.roll_btn.clicked.connect(self.toggle_roll)
        roll_btn_layout.addWidget(self.roll_btn)
        layout.addLayout(roll_btn_layout)
        
        # 功能按钮
        btn_layout1 = QHBoxLayout()
        btn_layout2 = QHBoxLayout()
        
        buttons = [
            ("隐藏", self.hide),
            ("置顶模式", self.open_simple_mode),
            ("修改名单", self.open_change_window),
            ("系统设置", self.open_settings),
            ("退出程序", self.close)
        ]
        
        for i, (text, slot) in enumerate(buttons):
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            
            if i < 2:
                btn_layout1.addWidget(btn)
            elif i < 4:
                btn_layout2.addWidget(btn)
            else:
                layout.addLayout(btn_layout1)
                layout.addLayout(btn_layout2)
                layout.addWidget(btn)
        
        layout.addStretch()
        self.setLayout(layout)

    def toggle_roll(self):
        """切换点名状态"""
        names = get_names()
        if not names:
            QMessageBox.warning(self, "名单为空", "请先添加名单数据")
            return
            
        if not self.is_rolling:
            # 开始新的一轮点名
            self.remaining_names = names.copy()
            random.shuffle(self.remaining_names)
            self.roll_interval = self.config["random"].get("min_speed", 50)
            
        self.is_rolling = not self.is_rolling
        self.roll_btn.setText("停止点名" if self.is_rolling else "开始点名")
        
        if self.is_rolling:
            self.timer.start(self.roll_interval)
        else:
            self.timer.stop()

    def open_simple_mode(self):
        """打开简约模式窗口"""
        from simple import SimpleCallWindow
        if self.simple_window is None:
            self.simple_window = SimpleCallWindow(self)
        self.hide()
        self.simple_window.show()
        logger.info("进入简约模式")

    def open_change_window(self):
        """安全打开名单管理窗口"""
        try:
            from change import ChangeListWindow
            if self.change_window is None:
                self.change_window = ChangeListWindow(self)
                self.change_window.names_changed.connect(self.on_names_changed)
            
            # 确保窗口正常显示
            self.change_window.show()
            self.change_window.raise_()
            self.change_window.activateWindow()
            logger.info("成功打开名单管理窗口")
            
        except ImportError as e:
            logger.error(f"导入模块失败: {e}")
            QMessageBox.critical(self, "错误", f"无法加载名单管理模块:\n{str(e)}")
        except Exception as e:
            logger.error(f"打开窗口失败: {e}")
            QMessageBox.critical(self, "错误", f"无法打开名单窗口:\n{str(e)}")
            # 重置窗口引用
            self.change_window = None

    def on_names_changed(self):
        """处理名单变化"""
        logger.info("检测到名单变化")
        if self.is_rolling:
            self.toggle_roll()
        self.remaining_names = []
        self.names_updated.emit()

    def open_settings(self):
        """打开设置窗口"""
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
            self.settings_window.theme_changed.connect(self.on_theme_changed)
            self.settings_window.setWindowModality(Qt.ApplicationModal)
        self.settings_window.show()
        logger.info("打开系统设置")

    def on_theme_changed(self, theme_config):
        """处理主题变更"""
        self.config["theme"] = theme_config
        self.apply_theme(theme_config)
        logger.info("主题设置已更新")

    def apply_theme(self, theme_config=None):
        """应用主题设置"""
        theme_config = theme_config or self.config["theme"]
        theme = theme_config.get("main", "light")
        style = theme_config.get("style", "classic")
        
        # 基础主题
        if theme == "dark":
            base_style = """
                QWidget {
                    background-color: #333333;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QListWidget {
                    background-color: #444444;
                    color: #FFFFFF;
                }
                QLineEdit {
                    background-color: #444444;
                    color: #FFFFFF;
                }
            """
        else:  # light or sys
            base_style = """
                QWidget {
                    background-color: #F5F5F5;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                QListWidget {
                    background-color: #FFFFFF;
                    color: #000000;
                }
                QLineEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                }
            """
        
        # 按钮风格
        if style == "retro":
            button_style = """
                QPushButton {
                    background-color: #8B4513;
                    color: white;
                    border: 2px groove #A0522D;
                    border-radius: 5px;
                    padding: 5px;
                    font-family: 'Courier New';
                }
                QPushButton:hover {
                    background-color: #A0522D;
                }
            """
        elif style == "modern":
            button_style = """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """
        elif style == "tech":
            button_style = """
                QPushButton {
                    background-color: #2C3E50;
                    color: #1ABC9C;
                    border: 1px solid #1ABC9C;
                    border-radius: 3px;
                    padding: 6px;
                    font-family: 'Consolas';
                }
                QPushButton:hover {
                    background-color: #34495E;
                }
            """
        else:  # classic
            button_style = """
                QPushButton {
                    background-color: #E0E0E0;
                    color: black;
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0;
                }
            """
        
        # 点名按钮特殊样式
        roll_button_style = """
            QPushButton#roll_btn {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton#roll_btn:hover {
                background-color: #45a049;
            }
        """
        
        # 结果标签样式
        result_label_style = """
            QLabel#result_label {
                color: #000000;
                background-color: rgba(255, 255, 255, 200);
                border-radius: 8px;
                padding: 20px;
                margin: 10px;
                min-height: 60px;
            }
        """
        
        self.setStyleSheet(base_style + button_style + roll_button_style + result_label_style)
        
        # 更新子窗口主题
        if self.simple_window:
            self.simple_window.apply_theme(self.config["theme"])
        if self.change_window:
            self.change_window.apply_theme(self.config["theme"])

    def init_tray_icon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme('applications-education'))
        
        tray_menu = QMenu()
        restore_action = tray_menu.addAction("恢复窗口")
        restore_action.triggered.connect(self.show_normal)
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("退出")
        exit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_normal(self):
        self.show()
        self.activateWindow()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出程序吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("应用程序退出")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    # 确保单实例运行
    if sys.platform == 'win32':
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "RandomCallMutex")
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.user32.MessageBoxW(0, "程序已经在运行中", "随机点名系统", 0x40)
            sys.exit(1)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont("Microsoft YaHei", 12))
    
    # 设置高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 主窗口
    window = MainWindow()
    window.show()
    
    logger.info("应用程序启动完成")
    sys.exit(app.exec_())
