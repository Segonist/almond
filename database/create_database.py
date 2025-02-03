import asyncio
from dotenv import load_dotenv
import os
from aiomysql import Connection, connect

load_dotenv("../.env")

ROOT_DIR = os.getenv("ROOT_DIR")
sql_file = f"{ROOT_DIR}/database/db_structure.sql"


async def get_db_connection() -> Connection:
    return await connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        db=os.getenv("DATABASE"),
        autocommit=True
    )


async def exec_sql_file(connection: Connection, sql_file: str):
    print(f"\n[INFO] Executing SQL script file: '{sql_file}'")
    statement = ""

    with open(sql_file, "r") as file:
        for line in file:
            if line.strip().startswith('--') or line.strip() == '':
                continue
            if not line.strip().endswith(';'):
                statement += line
            else:
                statement += line
                async with connection.cursor() as cursor:
                    await cursor.execute(statement)
                statement = ""


async def main():
    connection = await get_db_connection()
    try:
        await exec_sql_file(connection, sql_file)
    finally:
        connection.close()

asyncio.run(main())
