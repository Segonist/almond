import sqlite3
from config import config

ROOT_DIR = config["ROOT_DIR"]
with open(f"{ROOT_DIR}/database/db_structure.sql") as sql_file:
    sql = sql_file.read()

connection = sqlite3.connect(f"{ROOT_DIR}/database/almond.db")
cursor = connection.cursor()
cursor.executescript(sql)
connection.close()
