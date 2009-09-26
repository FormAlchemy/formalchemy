# -*- coding: utf-8 -*-
import pylons
import logging
log = logging.getLogger(__name__)

try:
    version = pylons.__version__.split('.')
except AttributeError:
    version = ['0', '6']

def format(environ, result):
    if environ.get('HTTP_ACCEPT', '') == 'application/json':
        result['format'] = 'json'
        return True
    elif 'format' not in result:
        result['format'] = 'html'
    return True

def admin_map(map, controller, url='%s'):
    """connect the admin controller `cls` under the given `url`"""
    log.info('connecting %s to %s' % (url, controller))
    map.connect('static_contents', '%s/static_contents/{id}' % url, controller=controller, action='static')

    map.connect('admin', '%s' % url,
        controller=controller, action='index')

    map.connect('formatted_admin', '%s.{format}' % url,
        controller=controller, action='index')

    map.connect("models", "%s/{modelname}" % url,
        controller=controller, action="edit", id=None, format='html',
        conditions=dict(method=["POST"], function=format))

    map.connect("models", "%s/{modelname}" % url,
        controller=controller, action="list",
        conditions=dict(method=["GET"], function=format))

    map.connect("formatted_models", "%s/{modelname}.{format}" % url,
        controller=controller, action="list",
        conditions=dict(method=["GET"]))

    map.connect("new_model", "%s/{modelname}/new" % url,
        controller=controller, action="edit", id=None,
        conditions=dict(method=["GET"]))

    map.connect("formatted_new_model", "%s/{modelname}/new.{format}" % url,
        controller=controller, action="edit", id=None,
        conditions=dict(method=["GET"]))

    map.connect("%s/{modelname}/{id}" % url,
        controller=controller, action="edit",
        conditions=dict(method=["PUT"], function=format))

    map.connect("%s/{modelname}/{id}" % url,
        controller=controller, action="delete",
        conditions=dict(method=["DELETE"]))

    map.connect("edit_model", "%s/{modelname}/{id}/edit" % url,
        controller=controller, action="edit",
        conditions=dict(method=["GET"]))

    map.connect("formatted_edit_model", "%s/{modelname}/{id}.{format}/edit" % url,
        controller=controller, action="edit",
        conditions=dict(method=["GET"]))

    map.connect("view_model", "%s/{modelname}/{id}" % url,
        controller=controller, action="edit",
        conditions=dict(method=["GET"], function=format))

    map.connect("formatted_view_model", "%s/{modelname}/{id}.{format}" % url,
        controller=controller, action="edit",
        conditions=dict(method=["GET"]))

