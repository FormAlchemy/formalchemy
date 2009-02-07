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
