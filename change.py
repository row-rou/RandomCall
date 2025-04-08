from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
import pandas as pd
from utils.database import (
    get_names, add_name, delete_name, 
    add_names, delete_names, clear_names
)
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChangeListWindow(QWidget):
    names_changed = pyqtSignal()  # 名单变化信号
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('名单管理')
        self.resize(600, 400)
        self.init_ui()
        self.load_names()
        
        if main_window:
            self.apply_theme(main_window.config["theme"])

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()

        # 标题
        title_label = QLabel("名单管理系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # 名单列表
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background: #2196F3;
                color: white;
            }
        """)
        layout.addWidget(self.list_widget)

        # 添加姓名部分
        add_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入姓名")
        self.name_edit.setStyleSheet("padding: 5px;")
        
        self.add_btn = QPushButton('添加')
        self.add_btn.setObjectName("add_btn")
        self.add_btn.clicked.connect(self.add_single_name)
        
        self.del_btn = QPushButton('删除')
        self.del_btn.setObjectName("del_btn")
        self.del_btn.clicked.connect(self.delete_selected_name)
        
        add_layout.addWidget(self.name_edit, stretch=1)
        add_layout.addWidget(self.add_btn)
        add_layout.addWidget(self.del_btn)
        layout.addLayout(add_layout)

        # 导入导出按钮
        import_export_layout = QHBoxLayout()
        
        self.import_excel_btn = QPushButton('导入Excel')
        self.import_excel_btn.setObjectName("import_btn")
        self.import_csv_btn = QPushButton('导入CSV')
        self.import_csv_btn.setObjectName("import_btn")
        self.import_txt_btn = QPushButton('导入TXT')
        self.import_txt_btn.setObjectName("import_btn")
        
        self.import_excel_btn.clicked.connect(lambda: self.import_names('excel'))
        self.import_csv_btn.clicked.connect(lambda: self.import_names('csv'))
        self.import_txt_btn.clicked.connect(lambda: self.import_names('txt'))
        
        self.export_excel_btn = QPushButton('导出Excel')
        self.export_csv_btn = QPushButton('导出CSV')
        self.export_txt_btn = QPushButton('导出TXT')
        
        self.export_excel_btn.clicked.connect(lambda: self.export_names('excel'))
        self.export_csv_btn.clicked.connect(lambda: self.export_names('csv'))
        self.export_txt_btn.clicked.connect(lambda: self.export_names('txt'))
        
        import_export_layout.addWidget(self.import_excel_btn)
        import_export_layout.addWidget(self.import_csv_btn)
        import_export_layout.addWidget(self.import_txt_btn)
        import_export_layout.addWidget(self.export_excel_btn)
        import_export_layout.addWidget(self.export_csv_btn)
        import_export_layout.addWidget(self.export_txt_btn)
        layout.addLayout(import_export_layout)

        # 底部操作按钮
        bottom_layout = QHBoxLayout()
        self.select_all_btn = QPushButton('全选')
        self.clear_all_btn = QPushButton('清空名单')
        
        self.select_all_btn.clicked.connect(self.select_all_names)
        self.clear_all_btn.clicked.connect(self.clear_all_names)
        
        bottom_layout.addWidget(self.select_all_btn)
        bottom_layout.addWidget(self.clear_all_btn)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def load_names(self):
        """加载名单列表"""
        try:
            self.list_widget.clear()
            names = get_names()
            if names:
                self.list_widget.addItems(names)
                logger.info(f"成功加载 {len(names)} 个姓名")
            else:
                self.list_widget.addItem("名单为空")
                logger.info("名单为空")
        except Exception as e:
            logger.error(f"加载名单失败: {e}")
            QMessageBox.critical(self, "错误", f"加载名单失败:\n{str(e)}")

    def add_single_name(self):
        """添加单个姓名"""
        name = self.name_edit.text().strip()
        if not name:
            return
            
        try:
            if add_name(name):
                self.list_widget.addItem(name)
                self.name_edit.clear()
                self.names_changed.emit()
                logger.info(f"成功添加姓名: {name}")
            else:
                QMessageBox.warning(self, '提示', '该姓名已存在！')
        except Exception as e:
            logger.error(f"添加姓名失败: {e}")
            QMessageBox.critical(self, "错误", f"添加姓名失败:\n{str(e)}")

    def delete_selected_name(self):
        """删除选中姓名"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先选择要删除的姓名')
            return
            
        try:
            names = [item.text() for item in selected_items]
            deleted_count = delete_names(names)
            if deleted_count > 0:
                for item in selected_items:
                    self.list_widget.takeItem(self.list_widget.row(item))
                self.names_changed.emit()
                logger.info(f"成功删除 {deleted_count} 个姓名")
            else:
                QMessageBox.warning(self, '提示', '删除失败，姓名可能不存在')
        except Exception as e:
            logger.error(f"删除姓名失败: {e}")
            QMessageBox.critical(self, "错误", f"删除姓名失败:\n{str(e)}")

    def select_all_names(self):
        """选择所有姓名"""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(True)

    def clear_all_names(self):
        """清空所有姓名"""
        reply = QMessageBox.question(
            self, '确认清空', 
            '确定要清空所有名单吗？此操作不可恢复！',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                if clear_names():
                    self.load_names()
                    self.names_changed.emit()
                    logger.info("成功清空名单")
            except Exception as e:
                logger.error(f"清空名单失败: {e}")
                QMessageBox.critical(self, "错误", f"清空名单失败:\n{str(e)}")

    def import_names(self, file_type):
        """导入名单"""
        file_filters = {
            'excel': 'Excel文件 (*.xlsx *.xls);;所有文件 (*.*)',
            'csv': 'CSV文件 (*.csv);;所有文件 (*.*)',
            'txt': '文本文件 (*.txt);;所有文件 (*.*)'
        }
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", file_filters[file_type])
        
        if not file_path:
            return
            
        try:
            # 读取文件
            if file_type == 'excel':
                df = pd.read_excel(file_path)
            elif file_type == 'csv':
                df = pd.read_csv(file_path)
            else:  # txt
                with open(file_path, 'r', encoding='utf-8') as f:
                    names = [line.strip() for line in f if line.strip()]
                    df = pd.DataFrame(names, columns=['Name'])
            
            # 获取姓名列
            new_names = df.iloc[:, 0].astype(str).dropna().unique().tolist()
            
            # 批量添加
            added = add_names(new_names)
            if added > 0:
                self.load_names()
                self.names_changed.emit()
                QMessageBox.information(self, "导入完成", 
                    f"成功导入 {added} 个姓名\n重复姓名已自动过滤")
                logger.info(f"成功导入 {added} 个姓名")
            else:
                QMessageBox.warning(self, "导入结果", 
                    "没有导入新姓名（可能全部已存在或文件为空）")
        except Exception as e:
            logger.error(f"导入失败: {e}")
            QMessageBox.critical(self, "导入错误", f"导入文件时出错:\n{str(e)}")

    def export_names(self, file_type):
        """导出名单"""
        file_filters = {
            'excel': 'Excel文件 (*.xlsx)',
            'csv': 'CSV文件 (*.csv)',
            'txt': '文本文件 (*.txt)'
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", file_filters[file_type])
        
        if not file_path:
            return
            
        try:
            names = get_names()
            if not names:
                QMessageBox.warning(self, "导出失败", "名单为空，无法导出")
                return
                
            df = pd.DataFrame(names, columns=['Name'])
            
            if file_type == 'excel':
                df.to_excel(file_path, index=False)
            elif file_type == 'csv':
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:  # txt
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(names))
            
            QMessageBox.information(self, "导出成功", "名单导出成功！")
            logger.info(f"成功导出名单到 {file_path}")
        except Exception as e:
            logger.error(f"导出失败: {e}")
            QMessageBox.critical(self, "导出错误", f"导出文件时出错:\n{str(e)}")

    def apply_theme(self, theme_config):
        """应用主题设置"""
        theme = theme_config.get("main", "light")
        style = theme_config.get("style", "classic")
        
        # 基础主题
        if theme == "dark":
            base_style = """
                QWidget {
                    background-color: #333333;
                    color: #FFFFFF;
                }
                QListWidget {
                    background-color: #444444;
                    color: #FFFFFF;
                    border: 1px solid #666666;
                }
                QLineEdit {
                    background-color: #444444;
                    color: #FFFFFF;
                    border: 1px solid #666666;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """
        else:  # light or sys
            base_style = """
                QWidget {
                    background-color: #F5F5F5;
                    color: #000000;
                }
                QListWidget {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                }
                QLineEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                }
                QLabel {
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
        
        # 特殊按钮样式
        special_button_style = """
            QPushButton#import_btn {
                background-color: #2196F3;
                color: white;
            }
            QPushButton#add_btn {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#del_btn {
                background-color: #f44336;
                color: white;
            }
        """
        
        self.setStyleSheet(base_style + button_style + special_button_style)

    def closeEvent(self, event):
        """关闭窗口时确保资源释放"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.quit()
        event.accept()
