import sqlite3
from dotenv import load_dotenv
import os

load_dotenv("../")

ROOT_DIR = os.getenv("ROOT_DIR")
with open(f"{ROOT_DIR}/database/db_structure.sql") as sql_file:
    sql = sql_file.read()

connection = sqlite3.connect(f"{ROOT_DIR}/database/almond.db")
cursor = connection.cursor()
cursor.executescript(sql)
connection.close()
