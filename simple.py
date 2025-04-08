from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QMouseEvent, QColor
from utils.database import get_names
import random

class SimpleCallWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.names = get_names()
        self.remaining_names = []
        self.init_ui()
        self.drag_pos = QPoint()
        self.apply_theme(self.main_window.config["theme"])
        
        # 点名定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_roll)
        self.is_running = False
        self.interval = 50

    def init_ui(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(
            self.main_window.config["simple_mode"].get("width", 320),
            self.main_window.config["simple_mode"].get("height", 220)
        )
        
        # 主背景（颜色将在apply_theme中设置）
        self.bg_style = ""
        self.setStyleSheet(self.bg_style)
        
        # 结果显示
        self.result_label = QLabel("准备就绪", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        self.result_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: rgba(0, 0, 0, 120);
                border-radius: 8px;
                padding: 15px;
                margin: 15px;
            }
        """)
        self.result_label.setGeometry(20, 20, 280, 100)
        
        # 操作按钮
        self.start_btn = QPushButton("开始点名", self)
        self.start_btn.setGeometry(60, 135, 100, 30)
        self.start_btn.clicked.connect(self.toggle_roll)
        
        # 返回主界面按钮
        self.return_btn = QPushButton("返回主界面", self)
        self.return_btn.setGeometry(160, 135, 100, 30)
        self.return_btn.clicked.connect(self.return_to_main)

    def toggle_roll(self):
        """切换点名状态"""
        if not self.names:
            QMessageBox.warning(self, "名单为空", "请先添加名单数据")
            return
            
        if not self.is_running:
            # 开始新的一轮点名
            self.remaining_names = self.names.copy()
            random.shuffle(self.remaining_names)
            self.interval = self.main_window.config["random"].get("min_speed", 50)
            
        self.is_running = not self.is_running
        self.start_btn.setText("停止" if self.is_running else "开始点名")
        
        if self.is_running:
            self.timer.start(self.interval)
        else:
            self.timer.stop()

    def update_roll(self):
        """更新点名滚动效果"""
        if not self.remaining_names:
            # 如果名单已空，重新加载
            self.remaining_names = get_names().copy()
            random.shuffle(self.remaining_names)
            
        # 随机选择一个名字
        selected_name = random.choice(self.remaining_names)
        self.result_label.setText(selected_name)
        
        # 从剩余名单中移除已点到的名字
        self.remaining_names.remove(selected_name)
        
        # 逐渐减慢速度
        max_speed = self.main_window.config["random"].get("max_speed", 200)
        self.interval = min(self.interval + 10, max_speed)
        self.timer.setInterval(self.interval)
        
        # 达到最大速度时停止
        if self.interval >= max_speed:
            self.toggle_roll()

    def apply_theme(self, theme_config):
        """应用主题设置"""
        theme = theme_config.get("simple", "dark")
        style = theme_config.get("style", "classic")
        bg_color = self.main_window.config["simple_mode"].get("bg_color", "#323232")
        opacity = self.main_window.config["simple_mode"].get("opacity", 200)
        
        # 背景主题（使用配置中的背景色和透明度）
        r, g, b, _ = QColor(bg_color).getRgb()
        self.bg_style = f"""
            background-color: rgba({r}, {g}, {b}, {opacity});
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 50);
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
                    background-color: rgba(255, 255, 255, 180);
                    color: #333;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 220);
                }
            """
        
        self.setStyleSheet(self.bg_style + button_style)

    def return_to_main(self):
        """返回主界面"""
        self.close()
        self.main_window.show()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
