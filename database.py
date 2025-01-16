import sqlite3
from time import time
from enum import Enum

connection = sqlite3.connect("almond.db")
cursor = connection.cursor()


class Response(Enum):
    DOES_NOT_EXIST = 0
    ALREADY_EXCISTS = 1
    SUCCESS = 2


def add_mode(name: str):
    # my implementation of case-insentivity
    name = name.lower()

    # check if there is such mode in database
    query = "SELECT 1 FROM mode WHERE name = ?;"
    response = cursor.execute(query, (name,))
    if response.fetchone() is not None:
        return Response.ALREADY_EXCISTS

    now = int(time())
    query = "INSERT INTO mode (name, created_at, updated_at) VALUES (?, ?, ?);"
    cursor.execute(query, (name, now, now,))
    connection.commit()
    return cursor.lastrowid


def edit_mode(old_name: str, new_name: str):
    old_name = old_name.lower()
    new_name = new_name.lower()

    # check if there is no mode with name new_name
    query = "SELECT 1 FROM mode WHERE name = ?;"
    response = cursor.execute(query, (new_name,))
    result = response.fetchone()
    if result is not None:
        return Response.ALREADY_EXCISTS

    # check if mode with name old_name exist
    query = "SELECT id FROM mode WHERE name = ?;"
    response = cursor.execute(query, (old_name,))
    result = response.fetchone()
    if result is None:
        return Response.DOES_NOT_EXIST

    now = int(time())
    mode_id = result[0]
    query = "UPDATE mode SET name = ?, updated_at = ? WHERE id = ?;"
    cursor.execute(query, (new_name, now, mode_id,))
    connection.commit()
    return Response.SUCCESS


def add_victory(user_id: int, mode: str):
    mode = mode.lower()

    # check if there is such mode in database
    query = "SELECT id FROM mode WHERE name = ?;"
    response = cursor.execute(query, (mode,))
    result = response.fetchone()
    if result is None:
        mode_id = add_mode(mode)
    else:
        mode_id = result[0]

    now = int(time())
    query = "INSERT INTO victory (discord_user_id, mode_id, created_at, updated_at) VALUES (?, ?, ?, ?);"
    cursor.execute(query, (user_id, mode_id, now, now))
    connection.commit()
    return Response.SUCCESS


def get_leaderboard(mode: str | None):
    if mode:
        query = "SELECT id FROM mode WHERE name = ?"
        response = cursor.execute(query, (mode,))
        result = response.fetchone()
        if not result:
            return Response.DOES_NOT_EXIST

        query = f"SELECT discord_user_id, COUNT(discord_user_id) as victories \
                FROM victory \
                WHERE mode_id = {result[0]} \
                GROUP BY discord_user_id \
                ORDER BY victories \
                DESC LIMIT 10;"
    else:
        query = "SELECT discord_user_id, COUNT(discord_user_id) as victories \
                FROM victory \
                GROUP BY discord_user_id \
                ORDER BY victories \
                DESC LIMIT 10;"
    response = cursor.execute(query)

    return response.fetchall()


def get_modes():
    query = "SELECT name FROM mode;"
    responce = cursor.execute(query)
    return responce.fetchall()
