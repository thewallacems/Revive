import difflib
import re

from database import tables

#  name: (id, ref)
cache = {}

_TABLES = {
    'Equips': tables.EquipsTable(),
    'Items': tables.ItemsTable(),
    'Monsters': tables.MonstersTable(),
}

_COLUMNS = {
    'level': 'level',
    'reqlevel': 'REQ_Level',
    'job': 'REQ_Job',
    'reqjob': 'REQ_Job',
    'str': 'STR',
    'reqstr': 'REQ_STR',
    'dex': 'DEX',
    'reqdex': 'REQ_DEX',
    'int': 'INT',
    'reqint': 'REQ_INT',
    'luk': 'LUK',
    'reqluk': 'REQ_LUK',
    'hp': 'HP',
    'mp': 'MP',
    'attackspeed': 'Attack_Speed',
    'as': 'Attack_Speed',
    'wa': 'Weapon_Attack',
    'weaponattack': 'Weapon_Attack',
    'watt': 'Weapon_Attack',
    'defense': 'Weapon_Defense',
    'def': 'Weapon_Defense',
    'wdef': 'Weapon_Defense',
    'weapondefense': 'Weapon_Defense',
    'ma': 'Magic_Attack',
    'matt': 'Magic_Attack',
    'magicattack': 'Magic_Attack',
    'avoid': 'Avoid',
    'eva': 'Avoid',
    'avoidability': 'Avoid',
    'accuracy': 'Accuracy',
    'acc': 'Accuracy',
    'speed': 'Speed',
    'spd': 'Speed',
    'jump': 'Jump',
    'slots': 'Slots',
    'npcprice': 'NPC_Price',
    'npc': 'NPC_Price',
    'price': 'Price',
    'hpr': 'HP_Recovery',
    'mpr': 'MP_Recovery',
    'hprecovery': 'HP_Recovery',
    'mprecovery': 'MP_Recovery',
    'success': 'Success',
    'knockback': 'Knockback',
    'attack': 'Attack'
}

SEARCH_REGEX = re.compile(r'^([A-Za-z]+)\s?([<>=]{1,2})\s?(\d+)$')


def _process_condition(condition):
    match = SEARCH_REGEX.match(condition)
    if not match:
        return None

    column = match.group(1).lower()
    if column not in _COLUMNS:
        return None

    column = _COLUMNS[column]
    operator = match.group(2)
    condition = match.group(3)

    return f'"{column}" {operator} {condition}'


async def _lookup(name, connection):
    lookup_table = tables.LookupsTable()
    query = lookup_table.select_lower()
    return await connection.fetchrow(query, name)


class Database:
    def __init__(self, pool):
        self.pool = pool

    async def where(self, table: str, condition: str):
        if not table.title() in _TABLES:
            return None

        table = _TABLES[table.title()]

        async with self.pool.acquire() as connection:
            conditions = condition.split(' ')
            matches = list(filter(lambda x: x is not None, map(_process_condition, conditions)))
            values = dict((match.split('=')[0].strip(), match.split('=')[1].strip()) for match in matches)

            query = table.select(values=values)
            names = map(lambda x: x['Name'], await connection.fetch(query, *map(int, values.values())))

            return names

    async def search(self, name: str):
        async with self.pool.acquire() as connection:
            if name in cache:
                id, ref = cache[name]
            else:
                lookup = await _lookup(name, connection)
                if lookup is None:
                    closest_names = await self._closest_matches(name)
                    return closest_names or None

                id = lookup['ID']
                ref = lookup['Ref']
                cache[name] = (id, ref)

            table = _TABLES[ref]
            values = {'"ID"': id}
            query = table.select(values=values)

            row = await connection.fetchrow(query, *values.values())
            return table.companion(*list(row.values())) if row else None

    async def _closest_matches(self, name):
        async with self.pool.acquire() as connection:
            table = tables.LookupsTable()
            query = table.select()
            names = map(lambda x: x['Name'], await connection.fetch(query))
            closest_names = difflib.get_close_matches(name, names)
            return closest_names
