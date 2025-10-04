from enum import Enum
from collections import namedtuple

from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Mode, Victory, UpdatableMessage


class Code(Enum):
    DOES_NOT_EXIST = 0
    ALREADY_EXISTS = 1
    SUCCESS = 2


class Response:
    def __init__(
        self,
        code: Code,
        data: list[Mode | Victory | UpdatableMessage]
        | Mode
        | Victory
        | UpdatableMessage = None,
    ):
        self.code = code
        self.data = data

    def __repr__(self) -> str:
        return f"Response(code={self.code}, data={self.data})"


async def create_mode(
    async_session: AsyncSession, guild_id: int, name: str
) -> Response:
    async with async_session() as session:
        session: AsyncSession

        # my implementation of case-insentivity
        name = name.lower()

        # check if there is such mode in database
        responce = await read_mode(async_session, guild_id, name)
        if responce.code is not Code.DOES_NOT_EXIST:
            return Response(Code.ALREADY_EXISTS)

        new_mode = Mode(name=name, guild_id=guild_id)
        session.add(new_mode)
        await session.commit()

    return Response(Code.SUCCESS, new_mode)


async def read_mode(async_session: AsyncSession, guild_id: int, name: str) -> Response:
    async with async_session() as session:
        session: AsyncSession

        # my vision of case-insentivity
        name = name.lower()

        statement = select(Mode).where(Mode.name == name, Mode.guild_id == guild_id)
        responce = await session.execute(statement)
        result = responce.scalar_one_or_none()
        if not result:
            return Response(Code.DOES_NOT_EXIST)

    return Response(Code.SUCCESS, result)


async def read_modes(async_session: AsyncSession, guild_id: int) -> Response:
    async with async_session() as session:
        session: AsyncSession

        statement = select(Mode).where(Mode.guild_id == guild_id)
        responce = await session.scalars(statement)
        result = responce.all()
    return Response(Code.SUCCESS, result)


async def update_mode(
    async_session: AsyncSession, guild_id: int, old_name: str, new_name: str
) -> Response:
    async with async_session() as session:
        session: AsyncSession

        # check if there is no mode with name new_name
        responce: Response = await read_mode(async_session, guild_id, new_name)
        if responce.code is not Code.DOES_NOT_EXIST:
            return Response(Code.ALREADY_EXISTS)

        # check if mode with name old_name exist
        responce = await read_mode(async_session, guild_id, old_name)
        if responce.code is not Code.SUCCESS:
            return Response(Code.DOES_NOT_EXIST)

        mode_id = responce.data.id
        statement = update(Mode).where(Mode.id == mode_id).values(name=new_name)
        await session.execute(statement)
        await session.commit()

    return Response(Code.SUCCESS)


async def create_victory(
    async_session: AsyncSession, guild_id: int, user_id: int, mode: str
) -> Response:
    async with async_session() as session:
        session: AsyncSession

        # check if there is such mode in database, if not - create it
        responce = await read_mode(async_session, guild_id, mode)

        if responce.code is Code.DOES_NOT_EXIST:
            responce = await create_mode(async_session, guild_id, mode)

        new_victory = Victory(user_id=user_id, mode=responce.data, guild_id=guild_id)
        session.add(new_victory)
        await session.commit()

    return Response(Code.SUCCESS)


async def delete_last_victory(async_session: AsyncSession, guild_id: int) -> Response:
    async with async_session() as session:
        session: AsyncSession

        # get last victory
        statement = (
            select(Victory)
            .options(selectinload(Victory.mode))
            .where(Victory.guild_id == guild_id)
            .order_by(Victory.id.desc())
            .limit(1)
        )
        responce = await session.execute(statement)
        result = responce.scalar_one_or_none()

        if not result:
            return Response(Code.DOES_NOT_EXIST)

        statement = delete(Victory).where(Victory.id == result.id)
        await session.execute(statement)
        await session.commit()

    return Response(Code.SUCCESS, result)


async def read_leaderboard(
    async_session: AsyncSession, guild_id: int, mode: str = None
) -> Response:
    async with async_session() as session:
        session: AsyncSession

        if mode:
            # check if there is such mode in database
            responce = await read_mode(async_session, guild_id, mode)
            if responce.code is Code.DOES_NOT_EXIST:
                return Response(Code.DOES_NOT_EXIST)

            statement = (
                select(Victory.user_id, func.count(Victory.user_id).label("victories"))
                .where(Victory.mode_id == responce.data.id)
                .where(Victory.guild_id == guild_id)
                .group_by(Victory.user_id)
                .order_by(desc("victories"))
            )
        else:
            statement = (
                select(Victory.user_id, func.count(Victory.user_id).label("victories"))
                .where(Victory.guild_id == guild_id)
                .group_by(Victory.user_id)
                .order_by(desc("victories"))
            )
        responce = await session.execute(statement)
        result = responce.fetchall()

        # TODO: make this an object
        LeaderboardRow = namedtuple("Leaderboard", ["user_id", "victories"])
        result = [LeaderboardRow(*row) for row in result]

    return Response(Code.SUCCESS, result)


async def create_updatable_message(
    async_session: AsyncSession,
    guild_id: int,
    channel_id: int,
    message_id: int,
    mode: str = None,
) -> Response:
    async with async_session() as session:
        session: AsyncSession

        if mode:
            # check if there is such mode in database
            responce = await read_mode(async_session, guild_id, mode)
            if responce.code is Code.DOES_NOT_EXIST:
                return Response(Code.DOES_NOT_EXIST)

            mode_id = responce.data.id
            statement = UpdatableMessage(
                channel_id=channel_id,
                message_id=message_id,
                mode_id=mode_id,
                guild_id=guild_id,
            )
        else:
            statement = UpdatableMessage(
                channel_id=channel_id, message_id=message_id, guild_id=guild_id
            )

        session.add(statement)
        await session.commit()

    return Response(Code.SUCCESS)


async def read_updatable_messages(
    async_session: AsyncSession, guild_id: int
) -> Response:
    session: AsyncSession

    async with async_session() as session:
        statement = (
            select(UpdatableMessage)
            .options(selectinload(UpdatableMessage.mode))  # Eagerly load Mode
            .where(UpdatableMessage.guild_id == guild_id)
        )
        responce = await session.scalars(statement)
        result = responce.all()
    return Response(Code.SUCCESS, result)


async def delete_updatable_message(
    async_session: AsyncSession, guild_id: int, channel_id: int, message_id: int
) -> Response:
    async with async_session() as session:
        session: AsyncSession

        statement = select(UpdatableMessage).where(
            UpdatableMessage.channel_id == channel_id,
            UpdatableMessage.message_id == message_id,
            UpdatableMessage.guild_id == guild_id,
        )
        responce = await session.execute(statement)
        result = responce.scalar_one_or_none()
        if not result:
            return Response(Code.DOES_NOT_EXIST)

        statement = delete(UpdatableMessage).where(
            UpdatableMessage.channel_id == channel_id,
            UpdatableMessage.message_id == message_id,
            UpdatableMessage.guild_id == guild_id,
        )
        await session.execute(statement)
        await session.commit()

    return Response(Code.SUCCESS)
