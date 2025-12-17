import aiosqlite
from uuid import uuid4, UUID
from bot.schemas.parcipant import GroupParcipant, GroupExclusion

DB_PATH = "secret_santa.db"
GROUP_TABLE_NAME = "groups"
PARCIPANTS_TABLE_NAME = "participants"
EXCLUSIONS_TABLE_NAME = "exclusions"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {GROUP_TABLE_NAME} (
            uuid       TEXT PRIMARY KEY,
            name     TEXT NOT NULL,
            owner_id INTEGER NOT NULL
        )
        """
        )
        await db.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {PARCIPANTS_TABLE_NAME} (
            group_id     TEXT NOT NULL,
            user_id      INTEGER,
            username     TEXT,
            wishlist     TEXT,
            ready        INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (group_id, user_id)
        )
        """
        )
        await db.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {EXCLUSIONS_TABLE_NAME} (
            group_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            excluded_username INTEGER NOT NULL,
            PRIMARY KEY (group_id, user_id, excluded_username)
        )
        """
        )
        await db.commit()


async def create_group(group_name: str, owner_id: str) -> UUID:
    sql = f"""
    INSERT INTO {GROUP_TABLE_NAME} (
        uuid,
        name,
        owner_id
    ) VALUES (?, ?, ?)
    """
    async with aiosqlite.connect(DB_PATH) as db:
        group_uuid = uuid4()
        await db.execute(sql, (str(group_uuid), group_name, owner_id))
        await db.commit()
    return group_uuid


async def add_parcipant_to_group(
    group_id: UUID, user_id: int | None, username: str, wishlist: str = ""
) -> None:
    sql = f"""
        INSERT INTO {PARCIPANTS_TABLE_NAME} (
            group_id,
            user_id,
            username,
            wishlist
        ) VALUES (?, ?, ?, ?)
    """
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(sql, (str(group_id), user_id, username, wishlist))
        await db.commit()


async def update_user_id_by_username_for_parcipant(
    group_id: UUID, user_id: int, username: int
) -> None:
    sql = f"""
    UPDATE {PARCIPANTS_TABLE_NAME} SET user_id = ? WHERE group_id = ? AND username = ?
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(sql, (user_id, str(group_id), username))
        await db.commit()


async def update_wishlist(group_id: str, user_id: int, wishlist: str) -> None:
    sql = f"""
        UPDATE {PARCIPANTS_TABLE_NAME} SET wishlist = ? WHERE group_id = ? AND user_id = ?
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(sql, (wishlist, group_id, user_id))
        await db.commit()


async def add_exclusion(group_id: UUID, user_id: int, excluded_username: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"""
        INSERT INTO {EXCLUSIONS_TABLE_NAME} (
            group_id,
            user_id,
            excluded_username
        ) VALUES (?, ?, ?)
        """,
            (str(group_id), user_id, excluded_username),
        )
        await db.commit()


async def set_ready(group_id: UUID, user_id: int) -> None:
    sql = f"""
        UPDATE {PARCIPANTS_TABLE_NAME} SET ready = 1 WHERE group_id = ? AND user_id = ?
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(sql, (group_id, user_id))
        await db.commit()


async def get_group_parcipants(group_id: str) -> list[GroupParcipant]:
    sql = f"""
    SELECT user_id, username, ready FROM {PARCIPANTS_TABLE_NAME} WHERE group_id = ?
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(sql, (group_id,))
        parcipants = await cursor.fetchall()
        return [
            GroupParcipant(
                user_id=parcipant[0], username=parcipant[1], ready=parcipant[2]
            )
            for parcipant in parcipants
        ]

async def get_group_exclusions(group_id: str) -> list[tuple[int, str]]:
    sql = f"""
        SELECT user_id, excluded_username FROM {EXCLUSIONS_TABLE_NAME} WHERE group_id = ?
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(sql, (group_id,))
        exclusions = await cursor.fetchall()
    return exclusions
