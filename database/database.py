from aiomysql import connect, Connection, DictCursor
from enum import Enum
from typing import Any
import os


class Code(Enum):
    DOES_NOT_EXIST = 0
    ALREADY_EXISTS = 1
    SUCCESS = 2


class Response:
    def __init__(self, code: Code, data: list[dict[str: Any]] | dict[str: Any] = None):
        self.code = code
        self.data = data


async def get_db_connection() -> Connection:
    return await connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        db=os.getenv("DB_NAME"),
        autocommit=True,
        cursorclass=DictCursor
    )


async def create_mode(guild_id: int, name: str) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    # my implementation of case-insentivity
    name = name.lower()

    # check if there is such mode in database
    responce = await read_mode_id(guild_id, name)
    if responce.code is not Code.DOES_NOT_EXIST:
        return Response(Code.ALREADY_EXISTS)

    query = "INSERT INTO mode (name, guild_id) VALUES (%s, %s);"
    await cursor.execute(query, (name, guild_id,))

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, {"id": cursor.lastrowid})


async def read_mode_id(guild_id: int, name: str) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    # my vision of case-insentivity
    name = name.lower()

    query = "SELECT id FROM mode WHERE name = %s AND guild_id = %s;"
    await cursor.execute(query, (name, guild_id,))
    result = await cursor.fetchone()
    if not result:
        return Response(Code.DOES_NOT_EXIST)

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)


async def read_modes(guild_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    query = "SELECT name FROM mode WHERE guild_id = %s;"
    await cursor.execute(query, (guild_id,))
    result = await cursor.fetchall()

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)


async def update_mode(guild_id: int, old_name: str, new_name: str) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    # check if there is no mode with name new_name
    responce = await read_mode_id(guild_id, new_name)
    if responce.code is not Code.DOES_NOT_EXIST:
        return Response(Code.ALREADY_EXISTS)

    # check if mode with name old_name exist
    responce = await read_mode_id(guild_id, old_name)
    if responce.code is not Code.SUCCESS:
        return Response(Code.DOES_NOT_EXIST)

    mode_id = responce.data["id"]
    query = "UPDATE mode SET name = %s WHERE id = %s;"
    await cursor.execute(query, (new_name, mode_id,))

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS)


async def create_victory(guild_id: int, user_id: int, mode: str) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    # check if there is such mode in database, if not - create it
    responce = await read_mode_id(guild_id, mode)
    if responce.code is Code.DOES_NOT_EXIST:
        responce = await create_mode(guild_id, mode)
    mode_id = responce.data["id"]

    query = "INSERT INTO victory (user_id, mode_id, guild_id) VALUES (%s, %s, %s);"
    await cursor.execute(query, (user_id, mode_id, guild_id,))

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS)


async def delete_last_victory(guild_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    # get last victory id
    query = "SELECT MAX(id) as id FROM victory WHERE guild_id = %s;"
    await cursor.execute(query, (guild_id,))
    result = await cursor.fetchone()
    last_id = result["id"]

    query = f"SELECT victory.user_id, mode.name \
            FROM victory \
            JOIN mode \
            ON victory.mode_id = mode.id \
            WHERE victory.id = {last_id} \
            AND victory.guild_id = %s;"
    await cursor.execute(query, (guild_id,))
    result = await cursor.fetchone()

    query = f"DELETE FROM victory WHERE id = {last_id};"
    await cursor.execute(query)

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)


async def read_leaderboard(guild_id: int, mode: str = None) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    if mode:
        # check if there is such mode in database
        responce = await read_mode_id(guild_id, mode)
        if responce.code is Code.DOES_NOT_EXIST:
            return Response(Code.DOES_NOT_EXIST)

        query = f"SELECT user_id, COUNT(user_id) as victories \
                FROM victory \
                WHERE mode_id = {responce.data['id']} \
                AND guild_id = %s \
                GROUP BY user_id \
                ORDER BY victories DESC;"
    else:
        query = "SELECT user_id, COUNT(user_id) as victories \
                FROM victory \
                WHERE guild_id = %s \
                GROUP BY user_id \
                ORDER BY victories DESC;"
    await cursor.execute(query, (guild_id,))
    result = await cursor.fetchall()

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)


async def create_updatable_message(guild_id: int, channel_id: int, message_id: int, mode: str = None) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    if mode:
        # check if there is such mode in database
        responce = await read_mode_id(guild_id, mode)
        if responce.code is Code.DOES_NOT_EXIST:
            return Response(Code.DOES_NOT_EXIST)

        mode_id = responce.data["id"]
        query = "INSERT INTO updatable_message (channel_id, message_id, mode_id, guild_id) VALUES (%s, %s, %s, %s);"
        await cursor.execute(query, (channel_id, message_id,
                                     mode_id, guild_id))
        return Response(Code.SUCCESS)

    query = "INSERT INTO updatable_message (channel_id, message_id, guild_id) VALUES (%s, %s, %s);"
    await cursor.execute(query, (channel_id, message_id, guild_id))

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS)


async def read_updatable_messages(guild_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    query = "SELECT updatable_message.channel_id, updatable_message.message_id, mode.name \
            FROM updatable_message \
            LEFT JOIN mode ON updatable_message.mode_id = mode.id \
            WHERE updatable_message.guild_id = %s;"
    await cursor.execute(query, (guild_id,))
    result = await cursor.fetchall()

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)


async def delete_updatable_message(guild_id: int, channel_id: int, message_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    query = "DELETE FROM updatable_message WHERE channel_id = %s AND message_id = %s AND guild_id = %s;"
    await cursor.execute(query, (channel_id, message_id, guild_id,))

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS)


async def create_role(guild_id: int, role_id: int, user_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    query = "INSERT INTO role (role_id, user_id, guild_id) VALUES (%s, %s, %s);"
    await cursor.execute(query, (role_id, user_id, guild_id))

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS)


async def read_role(guild_id: int, user_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    query = "SELECT role_id FROM role WHERE user_id = %s AND guild_id = %s;"
    await cursor.execute(query, (user_id, guild_id,))
    result = await cursor.fetchone()
    if not result:
        return Response(Code.DOES_NOT_EXIST)

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)


async def read_roles(guild_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    query = "SELECT role_id, user_id FROM role WHERE guild_id = %s;"
    await cursor.execute(query, (guild_id,))
    result = await cursor.fetchall()

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)


async def read_data_for_roles(guild_id: int) -> Response:
    connection = await get_db_connection()
    cursor: DictCursor = await connection.cursor()

    query = "SELECT victory.user_id, COUNT(victory.user_id) as victories, role.role_id \
            FROM victory \
            JOIN role ON victory.user_id = role.user_id \
            WHERE victory.guild_id = %s \
            GROUP BY victory.user_id \
            ORDER BY victories DESC;"
    await cursor.execute(query, (guild_id,))
    result = await cursor.fetchall()

    await cursor.close()
    connection.close()

    return Response(Code.SUCCESS, result)
