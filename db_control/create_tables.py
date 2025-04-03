# db_control/create_tables.py


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db_control.connect_MySQL import engine
from db_control import mymodels

def init_db():
    print("🔧 テーブル作成中...")
    mymodels.Base.metadata.create_all(bind=engine)
    print("✅ テーブル作成完了！")

if __name__ == "__main__":
    init_db()
