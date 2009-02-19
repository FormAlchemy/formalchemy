"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm

from pylonsapp.model import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    ## Reflected tables must be defined and mapped here
    #global reflected_table
    #reflected_table = sa.Table("Reflected", meta.metadata, autoload=True,
    #                           autoload_with=engine)
    #orm.mapper(Reflected, reflected_table)

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

animals_table = sa.Table("Animals", meta.metadata,
    sa.Column("id", sa.types.Integer, primary_key=True),
    sa.Column("name", sa.types.String(255), nullable=False),
    sa.Column("owner_id", sa.ForeignKey('Owners.id'), nullable=False),
    )

class Animal(object):
    def __repr__(self):
        return self.name

orm.mapper(Animal, animals_table)

owners_table = sa.Table("Owners", meta.metadata,
    sa.Column("id", sa.types.Integer, primary_key=True),
    sa.Column("name", sa.types.String(255), nullable=False),
    )

class Owner(object):
    def __repr__(self):
        return self.name

orm.mapper(Owner, owners_table, properties=dict(
           animals=orm.relation(Animal,
                                backref=orm.backref('owner', uselist=False))
           ))


## Non-reflected tables may be defined and mapped at module level
#foo_table = sa.Table("Foo", meta.metadata,
#    sa.Column("id", sa.types.Integer, primary_key=True),
#    sa.Column("bar", sa.types.String(255), nullable=False),
#    )
#
#class Foo(object):
#    pass
#
#orm.mapper(Foo, foo_table)


## Classes for reflected tables may be defined here, but the table and
## mapping itself must be done in the init_model function
#reflected_table = None
#
#class Reflected(object):
#    pass
