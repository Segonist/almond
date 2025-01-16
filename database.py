import sqlite3
from time import time
from enum import Enum

connection = sqlite3.connect("almond.db")
cursor = connection.cursor()


class Response(Enum):
    DOES_NOT_EXIST = 0
    ALREADY_EXCISTS = 1
    SUCCESS = 2


def add_game_mode(name: str):
    # my implementation of case-insentivity
    name = name.lower()

    # check if there is such game mode in database
    query = "SELECT 1 FROM game_mode WHERE name = ?;"
    response = cursor.execute(query, (name,))
    if response.fetchone() is not None:
        return Response.ALREADY_EXCISTS

    now = int(time())
    query = "INSERT INTO game_mode (name, created_at, updated_at) VALUES (?, ?, ?);"
    cursor.execute(query, (name, now, now,))
    connection.commit()
    return Response.SUCCESS


def edit_game_mode(old_name: str, new_name: str):
    old_name = old_name.lower()
    new_name = new_name.lower()

    # check if there is no game mode with name new_name
    query = "SELECT 1 FROM game_mode WHERE name = ?;"
    response = cursor.execute(query, (new_name,))
    result = response.fetchone()
    if result is not None:
        return Response.ALREADY_EXCISTS

    # check if game mode with name old_name exist
    query = "SELECT id FROM game_mode WHERE name = ?;"
    response = cursor.execute(query, (old_name,))
    result = response.fetchone()
    if result is None:
        return Response.DOES_NOT_EXIST

    now = int(time())
    game_mode_id = result[0]
    query = "UPDATE game_mode SET name = ?, updated_at = ? WHERE id = ?;"
    cursor.execute(query, (new_name, now, game_mode_id,))
    connection.commit()
    return Response.SUCCESS


def add_victory(user_id: int, game_mode: str):
    game_mode = game_mode.lower()

    # check if there is such game mode in database
    query = "SELECT id FROM game_mode WHERE name = ?;"
    response = cursor.execute(query, (game_mode,))
    result = response.fetchone()
    if result is None:
        return Response.DOES_NOT_EXIST

    now = int(time())
    game_mode_id = result[0]
    query = "INSERT INTO victory (discord_user_id, game_mode_id, created_at, updated_at) VALUES (?, ?, ?, ?);"
    cursor.execute(query, (user_id, game_mode_id, now, now))
    connection.commit()
    return Response.SUCCESS


def get_leaderboard(game_mode: str | None):
    if game_mode:
        query = "SELECT id FROM game_mode WHERE name = ?"
        response = cursor.execute(query, (game_mode,))
        result = response.fetchone()
        if not result:
            return Response.DOES_NOT_EXIST

        query = f"SELECT discord_user_id, COUNT(discord_user_id) as victories \
                FROM victory \
                WHERE game_mode_id = {result[0]} \
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


def get_game_modes():
    query = "SELECT name FROM game_mode;"
    responce = cursor.execute(query)
    return responce.fetchall()
