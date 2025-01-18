import sqlite3
from time import time
from enum import Enum
from typing import Any

connection = sqlite3.connect("./database/almond.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()


class Code(Enum):
    DOES_NOT_EXIST = 0
    ALREADY_EXISTS = 1
    SUCCESS = 2


class Response:
    def __init__(self, code: Code, data: list[dict[str: Any]] | dict[str: Any] = None):
        self.code = code
        self.data = data


def create_mode(guild_id: int, name: str) -> Response:
    # my implementation of case-insentivity
    name = name.lower()

    # check if there is such mode in database
    query = "SELECT 1 FROM mode WHERE name = ? AND guild_id = ?;"
    response = cursor.execute(query, (name, guild_id,))
    if response.fetchone() is not None:
        return Response(Code.ALREADY_EXISTS)

    now = int(time())
    query = "INSERT INTO mode (name, guild_id, created_at, updated_at) VALUES (?, ?, ?, ?);"
    cursor.execute(query, (name, guild_id, now, now,))
    connection.commit()
    return Response(Code.SUCCESS, {"mode_id": cursor.lastrowid})


def update_mode(guild_id: int, old_name: str, new_name: str) -> Response:
    old_name = old_name.lower()
    new_name = new_name.lower()

    # check if there is no mode with name new_name
    query = "SELECT 1 FROM mode WHERE name = ? AND guild_id = ?;"
    response = cursor.execute(query, (new_name, guild_id,))
    result = response.fetchone()
    if result is not None:
        return Response(Code.ALREADY_EXISTS)

    # check if mode with name old_name exist
    query = "SELECT id FROM mode WHERE name = ? AND guild_id = ?;"
    response = cursor.execute(query, (old_name, guild_id,))
    result = response.fetchone()
    if result is None:
        return Response(Code.DOES_NOT_EXIST)

    now = int(time())
    mode_id = result[0]
    query = "UPDATE mode SET name = ?, updated_at = ? WHERE id = ?;"
    cursor.execute(query, (new_name, now, mode_id,))
    connection.commit()
    return Response(Code.SUCCESS)


def create_victory(guild_id: int, user_id: int, mode: str) -> Response:
    mode = mode.lower()

    # check if there is such mode in database
    query = "SELECT id FROM mode WHERE name = ? AND guild_id = ?;"
    response = cursor.execute(query, (mode, guild_id,))
    result = response.fetchone()
    if result is None:
        mode_id = create_mode(guild_id, mode).data["mode_id"]
    else:
        mode_id = result[0]

    now = int(time())
    query = "INSERT INTO victory (discord_user_id, mode_id, guild_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, (user_id, mode_id, guild_id, now, now,))
    connection.commit()
    return Response(Code.SUCCESS)


def delete_last_victory(guild_id: int) -> Response:
    # get last victory id
    query = "SELECT MAX(id) FROM victory WHERE guild_id = ?;"
    responce = cursor.execute(query, (guild_id,))
    last_id = responce.fetchone()[0]

    query = f"SELECT victory.discord_user_id, mode.name \
            FROM victory \
            JOIN mode \
            ON victory.mode_id = mode.id \
            WHERE victory.id = {last_id} \
            AND victory.guild_id = ?;"
    responce = cursor.execute(query, (guild_id,))
    result = responce.fetchone()

    query = f"DELETE FROM victory WHERE id = {last_id};"
    cursor.execute(query)
    connection.commit()

    return Response(Code.SUCCESS, result)


def read_leaderboard(guild_id: int, mode: str = None) -> Response:
    if mode:
        # check if there is such mode in database
        query = "SELECT id FROM mode WHERE name = ? AND guild_id = ?;"
        response = cursor.execute(query, (mode, guild_id,))
        result = response.fetchone()
        if not result:
            return Response(Code.DOES_NOT_EXIST)

        query = f"SELECT discord_user_id, COUNT(discord_user_id) as victories \
                FROM victory \
                WHERE mode_id = {result['id']} \
                AND guild_id = ? \
                GROUP BY discord_user_id \
                ORDER BY victories \
                DESC LIMIT 10;"
    else:
        query = "SELECT discord_user_id, COUNT(discord_user_id) as victories \
                FROM victory \
                WHERE guild_id = ? \
                GROUP BY discord_user_id \
                ORDER BY victories \
                DESC LIMIT 10;"
    response = cursor.execute(query, (guild_id,))

    return Response(Code.SUCCESS, response.fetchall())


def read_modes(guild_id: int) -> Response:
    query = "SELECT name FROM mode WHERE guild_id = ?;"
    responce = cursor.execute(query, (guild_id,))
    data = [row["name"] for row in responce.fetchall()]
    return Response(Code.SUCCESS, data)
