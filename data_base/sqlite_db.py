import sqlite3 as sq
from aiogram.dispatcher import FSMContext
from aiogram import types
from create_bot import bot


base = sq.connect("karaoke")
cur = base.cursor()


def sql_start():

    if base:
        print("Data base connected OK!")

    base.execute(
        '''
        CREATE TABLE IF NOT EXISTS owners(
        karaoke_name TEXT PRIMARY KEY,
        karaoke_password TEXT,
        karaoke_avatar_id TEXT,
        owner_id TEXT,
        owner_first_name TEXT,
        owner_last_name TEXT,
        owner_username TEXT);
        '''
    )

    base.execute(
        '''
        CREATE TABLE IF NOT EXISTS visitors(
        user_id TEXT PRIMARY KEY,
        active_karaoke TEXT,
        karaoke_list TEXT);
        '''
    )

    base.execute(
        '''
        CREATE TABLE IF NOT EXISTS tracks(
            record_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id TEXT,
            active_karaoke TEXT,
            link TEXT);
        '''
    )

    base.commit()


async def sql_add_owner_record(state: FSMContext):

    async with state.proxy() as data:
        cur.execute("INSERT INTO owners VALUES(?, ?, ?, ?, ?, ?, ?)", tuple(data.values()))
        base.commit()


def sql_find_owner_id(karaoke_name: str):
    return cur.execute("SELECT owner_id FROM owners WHERE karaoke_name == ?", (karaoke_name,)).fetchone()[0]


def sql_find_karaoke_record(karaoke_name: str):
    return cur.execute("SELECT karaoke_avatar_id, karaoke_name, owner_username FROM owners WHERE karaoke_name == ?",
                       (karaoke_name,)).fetchone()


async def sql_add_user_record(user_id: str, active_karaoke: str, karaoke_name: str):
    cur.execute("INSERT INTO visitors VALUES(?, ?, ?)", (user_id, active_karaoke, karaoke_name))
    base.commit()


async def sql_update_user_record(user_id: str, active_karaoke: str, karaoke_list: list):
    cur.execute("UPDATE visitors SET active_karaoke == ?, karaoke_list == ? WHERE user_id == ?",
                (active_karaoke, '; '.join(karaoke_list), user_id))
    base.commit()


def sql_find_user_record(user_id: str):
    return cur.execute("SELECT active_karaoke, karaoke_list FROM visitors WHERE user_id == ?", (user_id,)).fetchone()


def sql_get_user_status(user_id: str):
    user_info = sql_find_user_record(user_id)
    owner_info = cur.execute("SELECT karaoke_name FROM owners WHERE owner_id == ?", (user_id,)).fetchall()
    return user_info, owner_info


async def sql_add_track_record(user_id: str, active_karaoke: str, link: str):

    if not table_is_empty("tracks"):
        cur.execute("INSERT INTO tracks(user_id, active_karaoke, link) VALUES(?, ?, ?)",
                    (user_id, active_karaoke, link))
    else:
        cur.execute("INSERT INTO tracks VALUES(?, ?, ?, ?)", (1, user_id, active_karaoke, link))
    base.commit()


def table_is_empty(table_name: str):
    return cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0] == 0
