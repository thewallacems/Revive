from dataclasses import dataclass

EMBED_COLOR = 0x71368a


def format_key_name(key):
    if '_' in key:
        key = ' '.join(key.split('_'))
    return key


def format_job(job_id):
    jobs = []
    if job_id - 8 >= 0:
        job_id -= 8
        jobs.append('Thief')
    if job_id - 4 >= 0:
        job_id -= 4
        jobs.append('Bowman')
    if job_id - 2 >= 0:
        job_id -= 2
        jobs.append('Magician')
    if job_id - 1 >= 0:
        job_id -= 1
        jobs.append('Warrior')
    if len(jobs) == 0:
        jobs.append('Common')
    jobs = reversed(jobs)
    return '/'.join(jobs)


def format_vars(obj):
    kv = vars(obj).copy()
    for key in ('Name', 'Description', 'ID', 'Effect', 'Cash', 'Undead',):
        if key in kv:
            kv.pop(key)

    drops_title = 'Drops' if 'Drops' in kv else 'Dropped By'
    drops = kv.pop('Drops', kv.pop('Dropped_By', []))
    drops = format_drops(drops)
    fields = [{'name': drops_title if index == 1 else '\U0000200b', 'value': drop, 'inline': True} for index, drop in
              enumerate(drops, 1) if drop] or None

    values = []
    for key, value in kv.items():
        if not value:
            continue

        if key == 'REQ_Job':
            value = format_job(value)
        if isinstance(value, int):
            value = f'{value:,}'

        values.append((key, value))

    description = '\n'.join((f'{format_key_name(key)}: {value}' for key, value in values))
    return fields, description


def format_drops(drops: str):
    line_count = 20

    chunks = []
    while drops.count('\n') > line_count:
        split_drops = drops.split('\n')
        chunk = '\n'.join(split_drops[:line_count])
        drops = '\n'.join(split_drops[line_count:])
        chunks.append(chunk)

    chunks.append(drops)
    return chunks


@dataclass()
class Equip:
    ID: int
    Cash: bool
    Name: str
    Description: str
    REQ_Level: int
    REQ_Job: int
    REQ_STR: int
    REQ_DEX: int
    REQ_INT: int
    REQ_LUK: int
    REQ_Fame: int
    STR: int
    DEX: int
    INT: int
    LUK: int
    HP: int
    MP: int
    Attack_Speed: int
    Weapon_Attack: int
    Weapon_Defense: int
    Magic_Attack: int
    Magic_Defense: int
    Avoid: int
    Accuracy: int
    Speed: int
    Jump: int
    Slots: int
    NPC_Price: int
    Dropped_By: str

    def to_embed_dict(self):
        fields, description = format_vars(self)
        title = self.Name
        if self.Cash:
            title += ' 💰'
        return {
            'title': title,
            'description': (self.Description or '') + f'\n\n{description}',
            'fields': fields,
            'color': EMBED_COLOR,
        }

    def get_image_url(self):
        id = f'0{self.ID}' if len(str(self.ID)) < 8 else str(self.ID)
        return f'https://lib.revivalstory.net/images/items/equips/{id}.png'


@dataclass
class Item:
    ID: int
    Name: str
    Description: str
    Effect: str
    Price: int
    HP: int
    MP: int
    HP_Recovery: int
    MP_Recovery: int
    Avoid: int
    Magic_Attack: int
    Weapon_Attack: int
    Weapon_Defense: int
    Success: int
    Magic_Defense: int
    Accuracy: int
    INT: int
    DEX: int
    Speed: int
    Jump: int
    STR: int
    Cash: bool
    LUK: int
    Dropped_By: str

    def to_embed_dict(self):
        description = ''
        if self.Description:
            description += self.Description
        if self.Effect:
            description += f'\n{self.Effect}'

        fields, desc = format_vars(self)
        title = f'💰 {self.Name}' if self.Cash else self.Name
        return {
            'title': title,
            'description': description + (f'\n\n{desc}' if desc else ''),
            'fields': fields,
            'color': EMBED_COLOR,
        }

    def get_image_url(self):
        id = f'0{self.ID}' if len(str(self.ID)) < 8 else str(self.ID)
        return f'https://lib.revivalstory.net/images/items/consume/{id}.png'


@dataclass
class Lookup:
    ID: int
    Name: str
    Ref: str


@dataclass
class Monster:
    ID: int
    Name: str
    Level: int
    HP: int
    MP: int
    Speed: int
    Attack: int
    Defense: int
    Magic_Attack: int
    Magic_Defense: int
    Accuracy: int
    Avoid: int
    XP: int
    Undead: bool
    Knockback: int
    Drops: str

    def to_embed_dict(self):
        fields, description = format_vars(self)
        description += f'\n\nHP/XP Ratio: {self.HP / self.XP:.2f}'
        title = f'{self.Name} 💀' if self.Undead else self.Name
        return {
            'title': title,
            'description': description,
            'fields': fields,
            'color': EMBED_COLOR,
        }

    def get_image_url(self):
        id = f'0{self.ID}' if len(str(self.ID)) < 7 else str(self.ID)
        return f'https://lib.revivalstory.net/images/monsters/{id}.png'
