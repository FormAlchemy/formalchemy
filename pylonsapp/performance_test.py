#!bin/python
import webob
import formalchemy
import sqlalchemy as sa
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

from repoze.profile.profiler import AccumulatingProfileMiddleware

def make_middleware(app):
    return AccumulatingProfileMiddleware(
        app,
        log_filename='/tmp/profile.log',
        discard_first_request=True,
        flush_at_shutdown=True,
        path='/__profile__')

Base = declarative_base()

class User(Base):
   __tablename__ = 'users'
   id = sa.Column(sa.Integer, primary_key=True)
   name = sa.Column(sa.Unicode(12))
   fullname = sa.Column(sa.Unicode(40))
   password = sa.Column(sa.Unicode(20))

def simple_app(environ, start_response):
    resp = webob.Response()
    fs = formalchemy.FieldSet(User)
    body = fs.bind(User()).render()
    body += fs.bind(User()).render()
    fs.rebind(User())
    body += fs.render()
    resp.body = body
    return resp(environ, start_response)

if __name__ == '__main__':
    import sys
    import os
    import signal
    from paste.httpserver import serve
    print 'Now do:'
    print 'ab -n 100 http://127.0.0.1:8080/'
    print 'wget -O - http://127.0.0.1:8080/__profile__'
    serve(make_middleware(simple_app))
