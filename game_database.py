import os
from urllib.parse import uses_netloc, urlparse

import peewee
from peewee import CharField, BigIntegerField

uses_netloc.append('postgres')
url = urlparse(os.environ["DATABASE_URL"])
db = peewee.PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname,
                               port=url.port)


class DatabaseModel(peewee.Model):
    class Meta:
        database = db

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Player(DatabaseModel):
    table_name = 'player'

    defaults = {
        'username': 'test',
        'password': 'random',
        'join_time': 1,
        'avatar_src': 'google.de',
        'clicks': 0
    }

    username = CharField(primary_key=True)
    password = CharField()
    join_time = BigIntegerField()
    avatar_src = CharField()
    clicks = BigIntegerField()

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return ', '.join((f'{name}: {self.__getattribute__(name)}' for name in self.get_attributes()))

    def __str__(self):
        return self.__repr__()

    def get_attributes(self):
        return self._meta.sorted_field_names

    @staticmethod
    def get_player(username):
        player = list(Player.select().where(Player.username == username))
        return player[0] if len(player) == 1 else None

    @staticmethod
    def create_player(**player):
        p = {**Player.defaults}
        for key, value in player.items():
            p[key] = value
        status = False
        try:
            return Player.create(**p)
        except peewee.IntegrityError:
            status = 'already exists'
        finally:
            print(f'Player with username {player.get("username")} {status if status else "created"}')

    @staticmethod
    def list():
        return list(Player.select())

    @staticmethod
    def set_player(player=None, **attrs):
        """
        Set a set of attributes from kwargs to player
        :param player: A username which is looked up in the db or a Player
        :param attrs: The attributes
        :return: 
        """
        if isinstance(player, str):
            player = Player.get_player(player)
        for attr in player.get_attributes():
            if attrs.get(attr, False):
                player.__setattr__(attr, attrs[attr])
        player.save()


db.create_tables([Player], safe=True)
