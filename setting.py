import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QSpinBox, QPushButton,
                            QMessageBox, QGroupBox, QTabWidget, QColorDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class SettingsWindow(QWidget):
    theme_changed = pyqtSignal(dict)  # 主题改变信号

    def __init__(self, config_path='config.json'):
        super().__init__()
        self.config_path = config_path
        self.config = self.load_config()
        self.init_ui()
        self.setWindowTitle('系统设置')
        self.resize(500, 450)
        self.apply_theme()

    def load_config(self):
        """加载配置文件"""
        default_config = {
            "theme": {
                "main": "light",
                "simple": "dark",
                "style": "classic"
            },
            "simple_mode": {
                "width": 320,
                "height": 220,
                "opacity": 200,
                "bg_color": "#323232"
            },
            "random": {
                "min_speed": 50,
                "max_speed": 200,
                "duration": 3000
            }
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            # 如果配置文件不存在，创建默认配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        except Exception as e:
            QMessageBox.warning(self, "配置错误", f"加载配置文件失败:\n{str(e)}")
            return default_config

    def save_config(self):
        """保存配置文件"""
        try:
            # 更新配置值
            self.config["theme"] = {
                "main": self.main_theme_combo.currentText(),
                "simple": self.simple_theme_combo.currentText(),
                "style": self.style_combo.currentText()
            }
            self.config["simple_mode"] = {
                "width": self.width_spin.value(),
                "height": self.height_spin.value(),
                "opacity": self.opacity_spin.value(),
                "bg_color": self.config["simple_mode"].get("bg_color", "#323232")
            }
            self.config["random"] = {
                "min_speed": self.min_speed_spin.value(),
                "max_speed": self.max_speed_spin.value(),
                "duration": self.duration_spin.value()
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            
            # 发送主题改变信号
            self.theme_changed.emit(self.config["theme"])
            
            QMessageBox.information(self, "成功", "配置已保存！")
            return True
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"无法保存配置:\n{str(e)}")
            return False

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # 主题设置标签页
        self.theme_tab = QWidget()
        self.init_theme_tab()
        self.tabs.addTab(self.theme_tab, "主题设置")

        # 简约模式设置标签页
        self.simple_tab = QWidget()
        self.init_simple_tab()
        self.tabs.addTab(self.simple_tab, "简约模式")

        # 随机设置标签页
        self.random_tab = QWidget()
        self.init_random_tab()
        self.tabs.addTab(self.random_tab, "随机设置")

        layout.addWidget(self.tabs)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_config)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def init_theme_tab(self):
        layout = QVBoxLayout()

        # 主界面主题
        main_group = QGroupBox("主界面主题")
        main_layout = QHBoxLayout()
        main_label = QLabel("主界面:")
        self.main_theme_combo = QComboBox()
        self.main_theme_combo.addItems(["light", "dark", "sys"])
        self.main_theme_combo.setCurrentText(self.config["theme"].get("main", "light"))
        main_layout.addWidget(main_label)
        main_layout.addWidget(self.main_theme_combo)
        main_group.setLayout(main_layout)
        layout.addWidget(main_group)

        # 简约模式主题
        simple_group = QGroupBox("简约模式主题")
        simple_layout = QHBoxLayout()
        simple_label = QLabel("简约模式:")
        self.simple_theme_combo = QComboBox()
        self.simple_theme_combo.addItems(["light", "dark", "sys"])
        self.simple_theme_combo.setCurrentText(self.config["theme"].get("simple", "dark"))
        simple_layout.addWidget(simple_label)
        simple_layout.addWidget(self.simple_theme_combo)
        simple_group.setLayout(simple_layout)
        layout.addWidget(simple_group)

        # 按钮风格
        style_group = QGroupBox("按钮风格")
        style_layout = QHBoxLayout()
        style_label = QLabel("风格:")
        self.style_combo = QComboBox()
        self.style_combo.addItems(["classic", "retro", "modern", "tech"])
        self.style_combo.setCurrentText(self.config["theme"].get("style", "classic"))
        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_combo)
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)

        layout.addStretch()
        self.theme_tab.setLayout(layout)

    def init_simple_tab(self):
        layout = QVBoxLayout()

        # 窗口设置
        window_group = QGroupBox("窗口设置")
        window_layout = QVBoxLayout()
        
        size_layout = QHBoxLayout()
        size_label = QLabel("窗口尺寸:")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 800)
        self.width_spin.setValue(self.config["simple_mode"].get("width", 320))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(150, 600)
        self.height_spin.setValue(self.config["simple_mode"].get("height", 220))
        size_layout.addWidget(size_label)
        size_layout.addWidget(QLabel("宽:"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("高:"))
        size_layout.addWidget(self.height_spin)
        window_layout.addLayout(size_layout)
        
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度(0-255):")
        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 255)
        self.opacity_spin.setValue(self.config["simple_mode"].get("opacity", 200))
        opacity_layout.addWidget(opacity_label)
        opacity_layout.addWidget(self.opacity_spin)
        window_layout.addLayout(opacity_layout)

        # 背景颜色设置
        color_layout = QHBoxLayout()
        color_label = QLabel("背景颜色:")
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.clicked.connect(self.choose_color)
        self.update_color_btn()
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_btn)
        window_layout.addLayout(color_layout)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)

        layout.addStretch()
        self.simple_tab.setLayout(layout)

    def init_random_tab(self):
        layout = QVBoxLayout()

        # 随机设置
        random_group = QGroupBox("随机点名设置")
        random_layout = QVBoxLayout()
        
        speed_layout = QHBoxLayout()
        speed_label = QLabel("速度范围(ms):")
        self.min_speed_spin = QSpinBox()
        self.min_speed_spin.setRange(10, 500)
        self.min_speed_spin.setValue(self.config["random"].get("min_speed", 50))
        self.max_speed_spin = QSpinBox()
        self.max_speed_spin.setRange(100, 1000)
        self.max_speed_spin.setValue(self.config["random"].get("max_speed", 200))
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(QLabel("最小:"))
        speed_layout.addWidget(self.min_speed_spin)
        speed_layout.addWidget(QLabel("最大:"))
        speed_layout.addWidget(self.max_speed_spin)
        random_layout.addLayout(speed_layout)
        
        duration_layout = QHBoxLayout()
        duration_label = QLabel("持续时间(ms):")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1000, 10000)
        self.duration_spin.setValue(self.config["random"].get("duration", 3000))
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spin)
        random_layout.addLayout(duration_layout)
        
        random_group.setLayout(random_layout)
        layout.addWidget(random_group)

        layout.addStretch()
        self.random_tab.setLayout(layout)

    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(QColor(self.config["simple_mode"].get("bg_color", "#323232")), self, "选择背景色")
        if color.isValid():
            self.config["simple_mode"]["bg_color"] = color.name()
            self.update_color_btn()

    def update_color_btn(self):
        """更新颜色按钮显示"""
        color = self.config["simple_mode"].get("bg_color", "#323232")
        self.color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #888;")

    def apply_theme(self):
        """应用主题到设置窗口本身"""
        theme = self.config["theme"].get("main", "light")
        style = self.config["theme"].get("style", "classic")
        
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
                QGroupBox {
                    border: 1px solid #666666;
                    color: #FFFFFF;
                    margin-top: 10px;
                }
                QComboBox, QSpinBox {
                    background-color: #444444;
                    color: #FFFFFF;
                    border: 1px solid #666666;
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
                QGroupBox {
                    border: 1px solid #CCCCCC;
                    color: #000000;
                    margin-top: 10px;
                }
                QComboBox, QSpinBox {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
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
        
        self.setStyleSheet(base_style + button_style)
