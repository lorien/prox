from peewee import *
from datetime import datetime
from playhouse import db_url
import os
from uuid import uuid4

SCHEMA_VERSION = 1
db_proxy = Proxy()


def init_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'var/prox.%d.sqlite' % SCHEMA_VERSION)
    connection_url = 'sqlite:///%s' % db_path
    db_proxy.initialize(db_url.connect(connection_url))
    if not os.path.exists(db_path):
        db_proxy.create_tables([Check], safe=True)
    return db_proxy


class Check(Model):
    id = UUIDField(primary_key=True, default=uuid4)
    created = DateField(default=datetime.utcnow, index=True)
    count_ok = IntegerField()
    count_fail = IntegerField()
    count_connect_fail = IntegerField()
    count_read_fail = IntegerField()
    count_data_fail = IntegerField()
    ops = TextField()

    class Meta:
        database = db_proxy
        db_table = 'prox_check'
