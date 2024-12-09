from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import subprocess  # 確保 subprocess 被匯入
import hashlib

# 建立一個 Flask 應用程式
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用於會話管理和 flash 消息

# SQLite 資料庫檔案路徑
db_file = 'stockinformation.db'


# 函數：檢查帳號是否存在
def username_exists(username):
    conn = sqlite3.connect('app.db')  # 使用 app.db 資料庫（account資料庫）
    c = conn.cursor()
    c.execute("SELECT * FROM account WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None


# 函數：將新帳號資訊儲存到資料庫
def create_account(username, password):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # 密碼加密
    c.execute("INSERT INTO account (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()


# 函數：檢查帳號和密碼是否匹配
def check_credentials(username, password):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM account WHERE username = ?", (username,))
    account = c.fetchone()
    conn.close()
    if account:
        # 檢查密碼是否匹配
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if account[2] == hashed_password:
            return True
    return False


def get_table_dates():
    """從 SQLite 獲取資料表名稱，並移除前綴，返回日期清單"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    # 移除表名中的 'ETF排行' 部分，僅保留日期
    dates = [name[0].replace('ETF排行', '') for name in tables if name[0] != 'sqlite_sequence']
    return dates


# 定義一個路徑(/)
@app.route('/')
def home():
    # 重新定向回首頁面
    return redirect(url_for('index'))


# 定義一個路徑(/index)
@app.route('/index')
def index():
    return render_template('index.html', username=session.get('username'))


# 登出頁面路由
@app.route('/logout')
def logout():
    session.pop('username', None)  # 清除 session 中的登入資訊
    flash("登出成功！", 'success')
    return redirect(url_for('index'))


# 註冊頁面路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 檢查帳號是否已經存在
        if username_exists(username):
            flash("已有帳號", 'error')
            return redirect(url_for('register'))

        # 檢查密碼是否一致
        if password != confirm_password:
            flash("密碼不一致", 'error')
            return redirect(url_for('register'))

        # 註冊帳號
        create_account(username, password)
        flash("註冊成功，請登入！", 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# 登入頁面路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 驗證帳號和密碼
        if check_credentials(username, password):
            session['username'] = username  # 記住用戶名（登入狀態）
            flash("登入成功！", 'success')
            return redirect(url_for('index'))
        else:
            flash("無此帳號或密碼錯誤", 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


# 定義一個路徑(/run_script)
@app.route('/run_script', methods=['POST'])
def run_script():
    if 'username' not in session:
        flash("請先進行登入", 'error')
        return redirect(url_for('login'))  # 未登入，跳轉到登入頁面
    # 執行外部 Python 檔案
    subprocess.run(['python', 'catch_ETF_volume.py'], capture_output=True, text=True)
    return render_template('result.html')


# 定義一個路徑(/back)
@app.route('/back', methods=['POST'])
def back():
    # 重新定向回首頁面
    return redirect(url_for('index'))


# 定義一個路徑(/to_volume)
@app.route('/to_volume', methods=['POST'])
def to_volume():
    # 定向至volume頁面
    return redirect(url_for('volume'))


# 定義一個路徑(/volume)
@app.route('/volume')
def volume():
    # 使用共用的函數獲取資料表日期
    dates = get_table_dates()
    return render_template('volume.html', dates=dates)


# 定義一個路徑(/data)
@app.route('/data', methods=['POST'])
def data():
    # 使用共用的函數獲取資料表日期
    dates = get_table_dates()

    # 獲取選單送出的值
    table_name = request.form.get('tables')

    # 完整的表名
    full_table_name = f"ETF排行{table_name}"

    # 查詢選定的資料表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM [{full_table_name}]")
    rows = cursor.fetchall()

    # 設定欄位名稱
    columns = ['日期', '排名', '股名', '股號', '股價', '最高', '最低', '價差', '成交量(張)']
    conn.close()

    return render_template('data.html', dates=dates, table_name=table_name, columns=columns, rows=rows)


# 確保程式直接執行時啟動伺服器
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
