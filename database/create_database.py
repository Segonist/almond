import sqlite3

with open("database/db_structure.sql") as sql_file:
    sql = sql_file.read()

connection = sqlite3.connect(f"database/almond.db")
cursor = connection.cursor()
cursor.executescript(sql)
connection.close()
