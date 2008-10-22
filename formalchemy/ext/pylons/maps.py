# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(__name__)

def admin_map(map, cls, url):
    """connect the admin controller `cls` under the given `url`"""
    cname = cls.__name__.lower().split('controller')[0]
    log.info('connecting %s to %s' % (url, cname))
    map.connect('/%s/' % url, controller=cname, action='index')
    map.connect('/%s/:modelname' % url, controller=cname, action='list')
    map.connect('/%s/:modelname/:action' % url, controller=cname)
    map.connect('/%s/:modelname/:action/:id' % url, controller=cname)
