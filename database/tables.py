from typing import Optional, List

from database import models

bool_keys = ('cash', 'quest', 'curse', 'darkness', 'poison', 'seal', 'weakness', 'pda', 'undead',)


def format_values(values, delimiter):
    ret = {}
    for key, value in values.items():
        if key in bool_keys:
            value = 't' if bool(value) else 'f'
        elif isinstance(value, str):
            value = f"'{value}'"
        ret[key] = value
    return delimiter.join((f'{key} = {value}' for key, value in ret.items()))


def write_values(values):
    ret = ''
    for key, value in values.items():
        if value is None:
            ret += 'null'
        elif key in bool_keys:
            ret += "'t'" if bool(value) else "'f'"
        elif isinstance(value, str):
            value = value.replace("'", "''")
            ret += f"'{value}'"
        else:
            ret += str(value)
        ret += ', '
    ret = ret[:-2]
    return ret


class BaseTable:
    def __init__(self, table: str, columns: List[str], companion: object):
        self.table = table
        self.columns = columns
        self.companion = companion

    def insert(self, values: dict):
        formatted_values = write_values(values)
        formatted_columns = ', '.join(self.columns)
        query = f'INSERT INTO "{self.table}"({formatted_columns}) VALUES({formatted_values});'
        return query

    def select(self, values: Optional[dict] = None):
        if values:
            formatted_values = format_values(values, ' AND ')
            query = f'SELECT * FROM "{self.table}" WHERE {formatted_values};'
        else:
            query = f'SELECT * FROM "{self.table}";'
        return query

    def select_lower(self):
        query = f'SELECT * FROM "{self.table}" WHERE lower("Name") = LOWER($1);'
        return query

    def update(self, new: dict, where: dict):
        formatted_new = format_values(new, ', ')
        formatted_where = format_values(where, ' AND ')
        query = f'UPDATE "{self.table}" SET {formatted_new} WHERE {formatted_where};'
        return query

    def delete(self, values: dict):
        formatted_values = format_values(values, ' AND ')
        query = f'DELETE FROM "{self.table}" WHERE {formatted_values};'
        return query


class EquipsTable(BaseTable):
    def __init__(self):
        table = 'Equips'
        columns = [f'"{col}"' for col in list(models.Equip.__annotations__.keys())]
        companion = models.Equip
        super().__init__(table, columns, companion)


class ItemsTable(BaseTable):
    def __init__(self):
        table = 'Items'
        columns = [f'"{col}"' for col in list(models.Item.__annotations__.keys())]
        companion = models.Item
        super().__init__(table, columns, companion)


class LookupsTable(BaseTable):
    def __init__(self):
        table = 'Lookups'
        columns = [f'"{col}"' for col in list(models.Lookup.__annotations__.keys())]
        companion = models.Lookup
        super().__init__(table, columns, companion)


class MonstersTable(BaseTable):
    def __init__(self):
        table = 'Monsters'
        columns = [f'"{col}"' for col in list(models.Monster.__annotations__.keys())]
        companion = models.Monster
        super().__init__(table, columns, companion)
