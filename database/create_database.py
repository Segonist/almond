import mariadb
from subprocess import Popen, PIPE
from dotenv import load_dotenv
import os

load_dotenv("../")
ROOT_DIR = os.getenv("ROOT_DIR")
sql_file = f"{ROOT_DIR}/database/db_structure.sql"


def exec_sql_file(cursor, sql_file):
    print(f"\n[INFO] Executing SQL script file: '{sql_file}'")
    statement = ""

    try:
        with open(sql_file, "r") as file:
            for line in file:
                if line.strip().startswith('--') or line.strip() == '':
                    continue
                if not line.strip().endswith(';'):
                    statement += line
                else:
                    statement += line
                    try:
                        cursor.execute(statement)
                        print(f"[INFO] Successfully executed statement:\n{
                              statement.strip()}")
                    except mariadb.Error as e:
                        print(f"[WARN] MariaDB Error during execution: {e}")
                    statement = ""
    except FileNotFoundError as e:
        print(f"[ERROR] SQL file not found: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")


connection = mariadb.connect(user=os.getenv("USER"),
                             password=os.getenv("PASSWORD"),
                             host=os.getenv("HOST"),
                             database=os.getenv("DATABASE"))
cursor = connection.cursor()

exec_sql_file(cursor, sql_file)

connection.close()
