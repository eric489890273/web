import sqlite3
import requests
from bs4 import BeautifulSoup as bs

# 抓取網頁內容
volumeweb = 'https://tw.stock.yahoo.com/tw-etf/volume'
res = requests.get(volumeweb)
soup = bs(res.text, 'lxml')

# 抓取表格類型
tabletype = soup.find(class_='Fz(24px) Fz(20px)--mobile Fw(b)')
tabletype = tabletype.get_text()
today = soup.find(class_='C(#6e7780) Fz(14px) As(fe)')
today = today.get_text()
today = today.replace('資料時間：', '')

# 設定資料表名稱
tablename = tabletype + today

# SQLite 資料庫連接（創建或打開本地資料庫檔案）
db_file = 'stockinformation.db'
conn = sqlite3.connect(db_file)

# 建立游標
cursor = conn.cursor()

# 若資料表存在，先刪除
cursor.execute(f"DROP TABLE IF EXISTS [{tablename}]")

# 創建一個資料表，用來存取今日抓取下來的資料
create_table_query = f'''
CREATE TABLE [{tablename}] (
    date DATE NOT NULL,
    ranking INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    number TEXT NOT NULL,
    price REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    Spread REAL NOT NULL,
    volume TEXT NOT NULL
)
'''
# 執行創建資料表
cursor.execute(create_table_query)

# 創建資料存取處
data = []

# 尋找網頁中的具有所需資料的列表並提取列資料
table = soup.find(class_='M(0) P(0) List(n)')
lines = table.find_all(class_='List(n)')

# 抓取每一列中的欄資料，再抓取日期並添加序號後加在每一列資料的最前面
for line in lines:
    cols = line.find_all('div')
    cols = [col.text.strip() for col in cols]
    data.append(cols)

# 過濾需要的資料
filter_data = [item[6:9] + item[11:15] for item in data]

# 將過濾過的資料依序插入資料表中
for record in filter_data:
    insert_query = f'''
    INSERT INTO [{tablename}](date, name, number, price, high, low, Spread, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(insert_query, (today, record[0], record[1], float(record[2]), float(record[3]), float(record[4]), float(record[5]), record[6]))

# 提交變更並關閉連接
conn.commit()
cursor.close()
conn.close()
