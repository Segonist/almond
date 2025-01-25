import sqlite3
from time import time
from enum import Enum
from typing import Any
import os

connection = sqlite3.connect(f"{os.getenv("ROOT_DIR")}/database/almond.db")
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
    responce = read_mode_id(guild_id, name)
    if responce.code is not Code.DOES_NOT_EXIST:
        return Response(Code.ALREADY_EXISTS)

    now = int(time())
    query = "INSERT INTO mode (name, guild_id, created_at, updated_at) VALUES (?, ?, ?, ?);"
    cursor.execute(query, (name, guild_id, now, now,))
    connection.commit()
    return Response(Code.SUCCESS, {"mode_id": cursor.lastrowid})


def read_mode_id(guild_id: int, name: str) -> Response:
    # my vision of case-insentivity
    name = name.lower()

    query = "SELECT id FROM mode WHERE name = ? AND guild_id = ?;"
    response = cursor.execute(query, (name, guild_id,))
    result = response.fetchone()
    if not result:
        return Response(Code.DOES_NOT_EXIST)
    return Response(Code.SUCCESS, dict(result))


def read_modes(guild_id: int) -> Response:
    query = "SELECT name FROM mode WHERE guild_id = ?;"
    responce = cursor.execute(query, (guild_id,))
    data = [dict(row) for row in responce.fetchall()]
    return Response(Code.SUCCESS, data)


def update_mode(guild_id: int, old_name: str, new_name: str) -> Response:
    # check if there is no mode with name new_name
    responce = read_mode_id(guild_id, new_name)
    if responce.code is not Code.DOES_NOT_EXIST:
        return Response(Code.ALREADY_EXISTS)

    # check if mode with name old_name exist
    responce = read_mode_id(guild_id, old_name)
    if responce.code is not Code.SUCCESS:
        return Response(Code.DOES_NOT_EXIST)

    now = int(time())
    mode_id = responce.data["id"]
    query = "UPDATE mode SET name = ?, updated_at = ? WHERE id = ?;"
    cursor.execute(query, (new_name, now, mode_id,))
    connection.commit()
    return Response(Code.SUCCESS)


def create_victory(guild_id: int, user_id: int, mode: str) -> Response:
    # check if there is such mode in database, if not - create it
    responce = read_mode_id(guild_id, mode)
    if responce.code is Code.DOES_NOT_EXIST:
        mode_id = create_mode(guild_id, mode).data["mode_id"]
    else:
        mode_id = responce.data["id"]

    now = int(time())
    query = "INSERT INTO victory (user_id, mode_id, guild_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, (user_id, mode_id, guild_id, now, now,))
    connection.commit()
    return Response(Code.SUCCESS)


def delete_last_victory(guild_id: int) -> Response:
    # get last victory id
    query = "SELECT MAX(id) as id FROM victory WHERE guild_id = ?;"
    responce = cursor.execute(query, (guild_id,))
    result = responce.fetchone()
    last_id = result["id"]

    query = f"SELECT victory.user_id, mode.name \
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

    return Response(Code.SUCCESS, dict(result))


def read_leaderboard(guild_id: int, mode: str = None) -> Response:
    if mode:
        # check if there is such mode in database
        responce = read_mode_id(guild_id, mode)
        if responce.code is Code.DOES_NOT_EXIST:
            return Response(Code.DOES_NOT_EXIST)

        query = f"SELECT user_id, COUNT(user_id) as victories \
                FROM victory \
                WHERE mode_id = {responce.data['id']} \
                AND guild_id = ? \
                GROUP BY user_id \
                ORDER BY victories DESC;"
    else:
        query = "SELECT user_id, COUNT(user_id) as victories \
                FROM victory \
                WHERE guild_id = ? \
                GROUP BY user_id \
                ORDER BY victories DESC;"
    response = cursor.execute(query, (guild_id,))
    result = response.fetchall()
    data = [dict(row) for row in result]

    return Response(Code.SUCCESS, data)


def create_updatable_message(guild_id: int, channel_id: int, message_id: int, mode: str = None) -> Response:
    now = int(time())
    if mode:
        # check if there is such mode in database
        responce = read_mode_id(guild_id, mode)
        if responce.code is Code.DOES_NOT_EXIST:
            return Response(Code.DOES_NOT_EXIST)

        mode_id = responce.data["id"]
        query = "INSERT INTO updatable_message (channel_id, message_id, mode_id, guild_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?);"
        cursor.execute(query, (channel_id, message_id,
                       mode_id, guild_id, now, now))
        connection.commit()
        return Response(Code.SUCCESS)

    query = "INSERT INTO updatable_message (channel_id, message_id, guild_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, (channel_id, message_id, guild_id, now, now))
    connection.commit()
    return Response(Code.SUCCESS)


def read_updatable_messages(guild_id: int) -> Response:
    query = "SELECT updatable_message.channel_id, updatable_message.message_id, mode.name \
            FROM updatable_message \
            LEFT JOIN mode ON updatable_message.mode_id = mode.id \
            WHERE updatable_message.guild_id = ?;"
    response = cursor.execute(query, (guild_id,))
    data = [dict(row) for row in response.fetchall()]
    return Response(Code.SUCCESS, data)


def delete_updatable_message(guild_id: int, channel_id: int, message_id: int) -> Response:
    query = "DELETE FROM updatable_message WHERE channel_id = ? AND message_id = ? AND guild_id = ?;"
    cursor.execute(query, (channel_id, message_id, guild_id,))
    connection.commit()
    return Response(Code.SUCCESS)


def create_role(guild_id: int, role_id: int, user_id: int) -> Response:
    now = int(time())
    query = "INSERT INTO role (role_id, user_id, guild_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(query, (role_id, user_id, guild_id, now, now))
    connection.commit()
    return Response(Code.SUCCESS)


def read_role(guild_id: int, user_id: int) -> Response:
    query = "SELECT role_id FROM role WHERE user_id = ? AND guild_id = ?;"
    response = cursor.execute(query, (user_id, guild_id,))
    result = response.fetchone()
    if not result:
        return Response(Code.DOES_NOT_EXIST)
    data = [dict(row) for row in result]
    return Response(Code.SUCCESS, data)


def read_roles(guild_id: int) -> Response:
    query = "SELECT role_id, user_id FROM role WHERE guild_id = ?;"
    response = cursor.execute(query, (guild_id,))
    data = [dict(row) for row in response.fetchall()]
    return Response(Code.SUCCESS, data)


def read_data_for_roles(guild_id: int) -> Response:
    query = "SELECT victory.user_id, COUNT(victory.user_id) as victories, role.role_id \
            FROM victory \
            JOIN role ON victory.user_id = role.user_id \
            WHERE victory.guild_id = ? \
            GROUP BY victory.user_id \
            ORDER BY victories DESC;"
    response = cursor.execute(query, (guild_id,))
    data = [dict(row) for row in response.fetchall()]
    return Response(Code.SUCCESS, data)
