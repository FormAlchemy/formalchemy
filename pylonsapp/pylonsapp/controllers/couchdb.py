__doc__ = """This is an example on ow to setup a CRUD UI with couchdb as
backend"""
import os
import logging
import pylonsapp
from couchdbkit import *
from webhelpers.paginate import Page
from pylonsapp.lib.base import BaseController, render
from couchdbkit.loaders import FileSystemDocsLoader
from formalchemy.ext import couchdb
from formalchemy.ext.pylons.controller import ModelsController

log = logging.getLogger(__name__)

class Person(couchdb.Document):
    """A Person node"""
    name = StringProperty(required=True)
    def __unicode__(self):
        return self.name or u''

class Pet(couchdb.Document):
    """A Pet node"""
    name = StringProperty(required=True)
    type = StringProperty(required=True)
    birthdate = DateProperty(auto_now=True)
    weight_in_pounds = IntegerProperty(default=0)
    spayed_or_neutered = BooleanProperty()
    owner = SchemaListProperty(Person)
    def __unicode__(self):
        return self.name

# You don't need a try/except. This is just to allow to run FA's tests without
# couchdb installed. Btw this have to be in another place in your app. eg: you
# don't need to sync views each time the controller is loaded.
try:
    server = Server()
    if server: pass
except:
    server = None
else:
    db = server.get_or_create_db('formalchemy_test')

    design_docs = os.path.join(os.path.dirname(pylonsapp.__file__), '_design')
    loader = FileSystemDocsLoader(design_docs)
    loader.sync(db, verbose=True)

    contain(db, Pet, Person)

class CouchdbController(BaseController):

    # override default classes to use couchdb fieldsets
    FieldSet = couchdb.FieldSet
    Grid = couchdb.Grid
    model = [Person, Pet]

    def Session(self):
        """return a formalchemy.ext.couchdb.Session"""
        return couchdb.Session(db)

CouchdbController = ModelsController(CouchdbController, prefix_name='couchdb', member_name='node', collection_name='nodes')
