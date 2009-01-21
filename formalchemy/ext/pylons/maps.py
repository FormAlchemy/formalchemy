# -*- coding: utf-8 -*-
import pylons
import logging
log = logging.getLogger(__name__)

try:
    version = pylons.__version__.split('.')
except AttributeError:
    version = ['0', '6']

def admin_map(map, controller, url='/admin'):
    """connect the admin controller `cls` under the given `url`"""
    log.info('connecting %s to %s' % (url, controller))
    if version > ['0', '7']:
        map.connect('%s' % url, controller=controller, action='index')
        map.connect('%s/' % url, controller=controller, action='index')
        map.connect('%s/static_contents/{id}' % url, controller=controller, action='static')
        map.connect('%s/{modelname}' % url, controller=controller, action='list')
        map.connect('%s/{modelname}/{action}' % url, controller=controller)
        map.connect('%s/{modelname}/{action}/{id}' % url, controller=controller)
    else:
        map.connect('%s' % url, controller=controller, action='index')
        map.connect('%s/' % url, controller=controller, action='index')
        map.connect('%s/static_contents/:id' % url, controller=controller, action='static')
        map.connect('%s/:modelname' % url, controller=controller, action='list')
        map.connect('%s/:modelname/:action' % url, controller=controller)
        map.connect('%s/:modelname/:action/:id' % url, controller=controller)

