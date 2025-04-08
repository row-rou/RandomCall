import PyInstaller.__main__
import os
import shutil
import sys

def build_app():
    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # 确保data目录存在
    data_dir = os.path.join('data')
    os.makedirs(data_dir, exist_ok=True)
    
    # PyInstaller配置
    pyinstaller_args = [
        'main.py',
        '--onefile',
        '--windowed',
        '--icon=app.ico',  # 替换为你的图标文件
        '--name=RandomCall',
        '--add-data=utils;utils',
        '--add-data=data;data',  # 包含data目录
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=pandas',
    ]
    
    # 执行打包
    PyInstaller.__main__.run(pyinstaller_args)
    
    print("打包完成！可执行文件在dist目录中")
    
    # 复制配置文件（如果需要）
    if os.path.exists('config.json'):
        shutil.copy2('config.json', os.path.join('dist', 'RandomCall'))

if __name__ == '__main__':
    build_app()
