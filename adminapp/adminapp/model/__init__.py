"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm

from adminapp.model import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    sm = orm.sessionmaker(autoflush=True, autocommit=False, bind=engine)

    meta.engine = engine
    meta.Session = orm.scoped_session(sm)

foo_table = sa.Table("Foo", meta.metadata,
    sa.Column("id", sa.types.Integer, primary_key=True),
    sa.Column("bar", sa.types.String(255), nullable=False),
    )

class Foo(object):
    pass

orm.mapper(Foo, foo_table)

files_table = sa.Table("Files", meta.metadata,
    sa.Column("id", sa.types.Integer, primary_key=True),
    sa.Column("path", sa.types.String(255), nullable=False),
    )

class Files(object):
    pass

orm.mapper(Files, files_table)


