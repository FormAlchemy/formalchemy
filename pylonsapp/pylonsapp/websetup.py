"""Setup the pylonsapp application"""
import logging

import pylons.test

from pylonsapp.config.environment import load_environment
from pylonsapp.model.meta import Session, metadata

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup pylonsapp here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they aren't there already
    metadata.create_all(bind=Session.bind)

    from pylonsapp import model

    o = model.Owner()
    o.name = 'gawel'
    Session.add(o)
    for i in range(50):
        o = model.Owner()
        o.name = 'owner%i' % i
        Session.add(o)
    Session.commit()

