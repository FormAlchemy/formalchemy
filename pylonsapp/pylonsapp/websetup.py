"""Setup the pylonsapp application"""
import logging

from pylonsapp.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup pylonsapp here"""
    load_environment(conf.global_conf, conf.local_conf)

    # Load the models
    from pylonsapp.model import meta
    meta.metadata.bind = meta.engine

    # Create the tables if they aren't there already
    meta.metadata.create_all(checkfirst=True)

    from pylonsapp import model

    o = model.Owner()
    o.name = 'gawel'
    meta.Session.add(o)
    for i in range(50):
        o = model.Owner()
        o.name = 'owner%i' % i
        meta.Session.add(o)
    meta.Session.commit()
