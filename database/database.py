import re

import asyncpg

import config
from database import tables

#  name: (id, ref)
cache = {}

_TABLES = {
    'Equips': tables.EquipsTable(),
    'Items': tables.ItemsTable(),
    'Monsters': tables.MonstersTable(),
}

NAME_TO_NAME = {
    'accuracy': 'Accuracy',
    'attack': 'Attack',
    'attackspeed': 'Attack_Speed',
    'avoidability': 'Avoid',
    'cash': 'Cash',
    'defense': 'Defense',
    'description': 'Description',
    'droppedby': 'Dropped_By',
    'drops': 'Drops',
    'eva': 'Avoid',
    'effect': 'Effect',
    'hp': 'HP',
    'hpr': 'HP_Recovery',
    'id': 'ID',
    'incacc': 'Accuracy',
    'inceva': 'Avoid',
    'incint': 'INT',
    'incjump': 'Jump',
    'incluk': 'LUK',
    'incdex': 'DEX',
    'incmad': 'Magic_Attack',
    'incmdd': 'Magic_Defense',
    'incmhp': 'HP',
    'incmmp': 'MP',
    'incpad': 'Weapon_Attack',
    'incpdd': 'Weapon_Defense',
    'incspeed': 'Speed',
    'incstr': 'STR',
    'knockback': 'Knockback',
    'level': 'Level',
    'mad': 'Magic_Attack',
    'magicattack': 'Magic_Attack',
    'magicdefence': 'Magic_Defense',
    'mp': 'MP',
    'mpr': 'MP_Recovery',
    'name': 'Name',
    'pad': 'Weapon_Attack',
    'pdd': 'Weapon_Defense',
    'price': 'Price',
    'ref': 'Ref',
    'reqdex': 'REQ_DEX',
    'reqint': 'REQ_INT',
    'reqjob': 'REQ_Job',
    'reqlevel': 'REQ_Level',
    'reqluk': 'REQ_LUK',
    'reqpop': 'REQ_Fame',
    'reqstr': 'REQ_STR',
    'speed': 'Speed',
    'success': 'Success',
    'undead': 'Undead',
    'xp': 'XP',
    'tuc': 'Slots',
}

SEARCH_REGEX = re.compile('^([A-Za-z]+)\s?([<>=]{1,2})\s?(\d+)$')


async def _lookup(name, connection):
    lookup_table = tables.LookupsTable()
    query = lookup_table.select_lower()
    return await connection.fetchrow(query, name)


class Database:
    def __init__(self):
        self.pool = None

    async def where(self, table: str, condition: str):
        async with self.pool.acquire() as connection:
            match = SEARCH_REGEX.match(condition)
            if not table.title() in _TABLES or not match:
                return None

            column = match.group(1)
            if not column.lower() in NAME_TO_NAME:
                return

            column = NAME_TO_NAME[column.lower()]
            operator = match.group(2)
            condition = match.group(3)

            query = f'SELECT * FROM "{table.title()}" WHERE "{column}" {operator} {condition};'
            return ', '.join(([f'`{record["Name"]}`' for record in await connection.fetch(query)]))

    async def search(self, name: str):
        async with self.pool.acquire() as connection:
            if name in cache:
                id, ref = cache[name]
            else:
                lookup = await _lookup(name, connection)
                if lookup is None:
                    return None

                id = lookup['ID']
                ref = lookup['Ref']
                cache[name] = (id, ref)

            table = _TABLES[ref]
            values = {'"ID"': id}
            query = table.select(values=values)
            row = await connection.fetchrow(query)
            if not row:
                return None

            return table.companion(*list(row.values()))

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            database=config.get('Database', 'Database'),
            user=config.get('Database', 'User'),
            host=config.get('Database', 'Host')
        )

    async def disconnect(self):
        await self.pool.close()
