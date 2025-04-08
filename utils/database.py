import os
import sqlite3
import sys
from typing import List, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.log')
)
logger = logging.getLogger(__name__)

def get_app_data_dir():
    """
    获取应用程序数据目录（兼容开发环境和打包后环境）
    打包后: ./data (与exe同目录)
    开发时: ./data (项目目录下)
    """
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件所在目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 确保data目录存在
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_db_path():
    """获取数据库完整路径"""
    return os.path.join(get_app_data_dir(), 'names.db')

DB_PATH = get_db_path()

def init_db():
    """初始化数据库表结构"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # 名单表
            conn.execute("""
            CREATE TABLE IF NOT EXISTS names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            """)
            # 点名历史表
            conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                called_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON names(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_time ON history(called_time)")
        logger.info(f"数据库初始化成功，路径: {DB_PATH}")
    except Exception as e:
        logger.critical(f"数据库初始化失败: {e}")
        raise RuntimeError(f"无法初始化数据库: {e}")

def get_connection():
    """获取数据库连接（自动重试机制）"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
        conn.execute("PRAGMA journal_mode = WAL")  # 使用WAL模式提高并发
        return conn
    except sqlite3.Error as e:
        logger.error(f"连接数据库失败: {e}")
        raise RuntimeError(f"无法连接数据库: {e}")

def get_names() -> List[str]:
    """获取所有姓名（按字母排序）"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM names ORDER BY name COLLATE NOCASE")
            names = [row[0] for row in cursor.fetchall()]
            logger.info(f"成功读取 {len(names)} 个姓名")
            return names
    except sqlite3.Error as e:
        logger.error(f"获取姓名列表失败: {e}")
        return []

def add_name(name: str) -> bool:
    """添加单个姓名"""
    if not name.strip():
        return False
        
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO names (name) VALUES (?)", (name.strip(),))
            conn.commit()
            logger.info(f"成功添加姓名: {name}")
            return True
    except sqlite3.IntegrityError:
        logger.warning(f"姓名已存在: {name}")
        return False
    except sqlite3.Error as e:
        logger.error(f"添加姓名失败: {e}")
        return False

def delete_name(name: str) -> bool:
    """删除单个姓名"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM names WHERE name=?", (name,))
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"成功删除姓名: {name}")
            else:
                logger.warning(f"姓名不存在: {name}")
            return deleted
    except sqlite3.Error as e:
        logger.error(f"删除姓名失败: {e}")
        return False

def delete_names(names: List[str]) -> int:
    """批量删除姓名（返回成功删除的数量）"""
    if not names:
        return 0
        
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "DELETE FROM names WHERE name=?",
                [(name,) for name in names]
            )
            conn.commit()
            deleted_count = cursor.rowcount
            logger.info(f"成功删除 {deleted_count} 个姓名")
            return deleted_count
    except sqlite3.Error as e:
        logger.error(f"批量删除姓名失败: {e}")
        return 0

def add_names(names: List[str]) -> int:
    """批量添加姓名（返回成功添加的数量）"""
    if not names:
        return 0
        
    # 过滤空姓名和已存在的姓名
    existing = set(get_names())
    new_names = [
        (name.strip(),) 
        for name in names 
        if name.strip() and name.strip() not in existing
    ]
    
    if not new_names:
        return 0
        
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO names (name) VALUES (?)",
                new_names
            )
            conn.commit()
            added_count = cursor.rowcount
            logger.info(f"成功批量添加 {added_count} 个姓名")
            return added_count
    except sqlite3.Error as e:
        logger.error(f"批量添加姓名失败: {e}")
        return 0

def clear_names() -> bool:
    """清空所有姓名"""
    try:
        with get_connection() as conn:
            conn.execute("DELETE FROM names")
            conn.commit()
            logger.info("成功清空姓名表")
            return True
    except sqlite3.Error as e:
        logger.error(f"清空姓名表失败: {e}")
        return False

def record_called_name(name: str) -> bool:
    """记录被点到的姓名"""
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO history (name) VALUES (?)", (name,))
            conn.commit()
            logger.info(f"记录点名: {name}")
            return True
    except sqlite3.Error as e:
        logger.error(f"记录点名失败: {e}")
        return False

def get_called_history(limit: int = 50) -> List[Tuple[str, str]]:
    """获取点名历史记录（最新50条）"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, strftime('%Y-%m-%d %H:%M:%S', called_time) 
                FROM history 
                ORDER BY called_time DESC 
                LIMIT ?
            """, (limit,))
            history = cursor.fetchall()
            logger.info(f"获取 {len(history)} 条历史记录")
            return history
    except sqlite3.Error as e:
        logger.error(f"获取历史记录失败: {e}")
        return []

def backup_database(backup_path: str = None) -> bool:
    """备份数据库到指定路径"""
    try:
        if not backup_path:
            backup_dir = os.path.join(get_app_data_dir(), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(
                backup_dir,
                f"names_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
        # 使用SQLite备份API
        with sqlite3.connect(DB_PATH) as src:
            with sqlite3.connect(backup_path) as dst:
                src.backup(dst)
        logger.info(f"数据库备份成功: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"数据库备份失败: {e}")
        return False

# 初始化数据库（如果不存在）
if not os.path.exists(DB_PATH):
    try:
        init_db()
    except Exception as e:
        logger.critical(f"程序启动失败 - 无法初始化数据库: {e}")
        raise RuntimeError(f"无法初始化数据库: {e}")
