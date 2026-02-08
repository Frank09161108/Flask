import sqlite3
import os
from typing import List, Optional, Any, Dict
import pandas as pd


class SQLiteManager:
    """SQLite数据库管理类"""

    def __init__(self, db_path: str = "my_database.db"):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"成功连接到数据库: {self.db_path}")
            return True
        except Exception as e:
            print(f"连接数据库失败: {e}")
            return False

    def create_database(self, overwrite: bool = False):
        """
        创建数据库文件

        Args:
            overwrite: 是否覆盖已存在的数据库
        """
        if overwrite and os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"已删除旧数据库: {self.db_path}")

        self.connect()
        print(f"数据库已创建: {self.db_path}")

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """
        创建数据表

        Args:
            table_name: 表名
            columns: 列名和类型的字典，如 {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
        """
        if not self.conn:
            self.connect()

        # 构建创建表的SQL语句
        columns_sql = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"

        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print(f"表 '{table_name}' 创建成功")
        except Exception as e:
            print(f"创建表失败: {e}")

    def insert_data(self, table_name: str, data: Dict[str, Any]):
        """
        插入单条数据

        Args:
            table_name: 表名
            data: 数据字典，如 {"name": "张三", "age": 25, "email": "zhangsan@example.com"}
        """
        if not self.conn:
            self.connect()

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
            print(f"数据插入成功，ID: {self.cursor.lastrowid}")
        except Exception as e:
            print(f"插入数据失败: {e}")

    def insert_many(self, table_name: str, data_list: List[Dict[str, Any]]):
        """
        批量插入数据

        Args:
            table_name: 表名
            data_list: 数据字典列表
        """
        if not data_list:
            return

        if not self.conn:
            self.connect()

        # 使用第一条数据确定列名
        columns = ", ".join(data_list[0].keys())
        placeholders = ", ".join(["?" for _ in data_list[0]])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            # 提取所有值
            values = [tuple(item.values()) for item in data_list]
            self.cursor.executemany(sql, values)
            self.conn.commit()
            print(f"批量插入成功，共插入 {len(data_list)} 条数据")
        except Exception as e:
            print(f"批量插入失败: {e}")

    def query(self, sql: str, params: tuple = None) -> List[tuple]:
        """
        执行查询语句

        Args:
            sql: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        if not self.conn:
            self.connect()

        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            # 获取列名
            column_names = [description[0] for description in self.cursor.description]

            # 获取所有数据
            rows = self.cursor.fetchall()

            # 组合列名和数据
            result = []
            for row in rows:
                result.append(dict(zip(column_names, row)))

            return result

        except Exception as e:
            print(f"查询失败: {e}")
            return []

    def query_with_pandas(self, sql: str, params: tuple = None) -> pd.DataFrame:
        """
        使用pandas执行查询

        Args:
            sql: SQL查询语句
            params: 查询参数

        Returns:
            pandas DataFrame
        """
        try:
            if params:
                df = pd.read_sql_query(sql, self.conn, params=params)
            else:
                df = pd.read_sql_query(sql, self.conn)
            return df
        except Exception as e:
            print(f"使用pandas查询失败: {e}")
            return pd.DataFrame()

    def execute(self, sql: str, params: tuple = None):
        """
        执行非查询SQL语句（INSERT, UPDATE, DELETE等）

        Args:
            sql: SQL语句
            params: 参数
        """
        if not self.conn:
            self.connect()

        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            self.conn.commit()
            print(f"SQL执行成功: {sql[:50]}...")
        except Exception as e:
            print(f"SQL执行失败: {e}")

    def get_table_info(self, table_name: str) -> List[tuple]:
        """
        获取表结构信息

        Args:
            table_name: 表名

        Returns:
            表结构信息
        """
        sql = f"PRAGMA table_info({table_name})"
        return self.query(sql)

    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        result = self.query(sql)
        return [table['name'] for table in result if table['name'] != 'sqlite_sequence']

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 示例使用函数
def create_sample_database():
    """创建示例数据库和表"""
    db = SQLiteManager("example.db")
    db.create_database(overwrite=True)

    # 创建用户表
    users_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "age": "INTEGER",
        "email": "TEXT UNIQUE",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    db.create_table("users", users_columns)

    # 创建订单表
    orders_columns = {
        "order_id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id": "INTEGER",
        "product": "TEXT NOT NULL",
        "amount": "REAL",
        "order_date": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "FOREIGN KEY (user_id)": "REFERENCES users(id)"
    }
    db.create_table("orders", orders_columns)

    return db


def insert_sample_data(db: SQLiteManager):
    """插入示例数据"""
    # 插入用户数据
    users_data = [
        {"name": "张三", "age": 25, "email": "zhangsan@example.com"},
        {"name": "李四", "age": 30, "email": "lisi@example.com"},
        {"name": "王五", "age": 28, "email": "wangwu@example.com"},
        {"name": "赵六", "age": 35, "email": "zhaoliu@example.com"}
    ]
    db.insert_many("users", users_data)

    # 插入订单数据
    orders_data = [
        {"user_id": 1, "product": "笔记本电脑", "amount": 5999.99},
        {"user_id": 1, "product": "鼠标", "amount": 199.50},
        {"user_id": 2, "product": "手机", "amount": 3999.00},
        {"user_id": 3, "product": "平板电脑", "amount": 2999.00},
        {"user_id": 4, "product": "耳机", "amount": 899.00},
        {"user_id": 4, "product": "键盘", "amount": 499.00}
    ]
    db.insert_many("orders", orders_data)


def demo_queries(db: SQLiteManager):
    """演示各种查询操作"""
    print("\n" + "=" * 50)
    print("演示查询操作")
    print("=" * 50)

    # 1. 查询所有用户
    print("\n1. 所有用户：")
    users = db.query("SELECT * FROM users")
    for user in users:
        print(f"  ID: {user['id']}, 姓名: {user['name']}, 年龄: {user['age']}, 邮箱: {user['email']}")

    # 2. 条件查询：年龄大于28的用户
    print("\n2. 年龄大于28的用户：")
    older_users = db.query("SELECT * FROM users WHERE age > ?", (28,))
    for user in older_users:
        print(f"  姓名: {user['name']}, 年龄: {user['age']}")

    # 3. 连接查询：用户及其订单
    print("\n3. 用户订单详情：")
    user_orders = db.query("""
        SELECT u.name, u.email, o.product, o.amount, o.order_date
        FROM users u
        JOIN orders o ON u.id = o.user_id
        ORDER BY u.name, o.order_date
    """)
    for order in user_orders:
        print(f"  用户: {order['name']}, 产品: {order['product']}, 金额: ¥{order['amount']}")

    # 4. 聚合查询：统计信息
    print("\n4. 统计信息：")
    stats = db.query("""
        SELECT 
            COUNT(*) as total_users,
            AVG(age) as avg_age,
            MAX(age) as max_age,
            MIN(age) as min_age
        FROM users
    """)[0]
    print(f"  总用户数: {stats['total_users']}")
    print(f"  平均年龄: {stats['avg_age']:.1f}")
    print(f"  最大年龄: {stats['max_age']}")
    print(f"  最小年龄: {stats['min_age']}")

    # 5. 使用pandas查询
    print("\n5. 使用pandas查询（用户消费总额）：")
    df = db.query_with_pandas("""
        SELECT 
            u.name,
            u.email,
            COUNT(o.order_id) as order_count,
            SUM(o.amount) as total_amount
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id
        ORDER BY total_amount DESC
    """)
    print(df.to_string(index=False))

    # 6. 表结构信息
    print("\n6. users表结构：")
    table_info = db.get_table_info("users")
    for col in table_info:
        print(f"  列名: {col['name']}, 类型: {col['type']}, 允许空: {'否' if col['notnull'] else '是'}")


def simple_query_example():
    """最简单的查询示例"""
    print("\n" + "=" * 50)
    print("快速入门示例")
    print("=" * 50)

    # 方法1：使用上下文管理器（推荐）
    with SQLiteManager("example.db") as db:
        # 简单查询
        result = db.query("SELECT name, age FROM users WHERE age BETWEEN ? AND ?", (25, 32))
        for row in result:
            print(f"姓名: {row['name']}, 年龄: {row['age']}")

    # 方法2：手动管理
    db = SQLiteManager("example.db")
    db.connect()

    try:
        # 执行自定义SQL
        db.execute("UPDATE users SET age = age + 1 WHERE name = ?", ("张三",))

        # 查询更新后的数据
        updated = db.query("SELECT * FROM users WHERE name = ?", ("张三",))
        print(f"\n更新后的数据: {updated}")

    finally:
        db.close()


# 主程序
if __name__ == "__main__":
    print("SQLite3 数据库操作示例")
    print("=" * 50)

    # 创建数据库和表
    db = create_sample_database()

    # 插入数据
    insert_sample_data(db)

    # 演示查询
    demo_queries(db)

    # 简单示例
    simple_query_example()

    # 关闭连接
    db.close()

    print("\n" + "=" * 50)
    print("数据库文件已保存为: example.db")
    print("可以使用DB Browser for SQLite等工具打开查看")