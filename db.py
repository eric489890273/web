import sqlite3

def init_account_db():
    conn = sqlite3.connect('app.db')  # 用來儲存帳號資料
    c = conn.cursor()
    # 創建 account 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_account_db()
