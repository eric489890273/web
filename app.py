from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import subprocess  # 確保 subprocess 被匯入

# 建立一個 Flask 應用程式
app = Flask(__name__)

# SQLite 資料庫檔案路徑
db_file = 'stockinformation.db'


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
    return render_template('index.html')


# 定義一個路徑(/run_script)
@app.route('/run_script', methods=['POST'])
def run_script():
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
