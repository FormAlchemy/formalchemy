# -*- coding: utf-8 -*-

def admin_map(map, controller):
    map.connect('%s/:action/:modelname/:id' % controller,
                controller=controller)

