# Copyright (C) 2007 Alexandre Conrad, alexandre (dot) conrad (at) gmail (dot) com
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
from gettext import GNUTranslations

i18n_path = os.path.join(os.path.dirname(__file__), 'i18n_resources')

try:
    from pylons.i18n import get_lang
    HAS_PYLONS = True
except:
    HAS_PYLONS = False

if not HAS_PYLONS:
    def get_lang(): return []

class _Translator(object):
    """dummy translator"""
    def gettext(self, value):
        return value

def get_translator(lang=None):
    """
    return a GNUTranslations instance for `lang`::

        >>> translator = get_translator('fr')
        ... assert translator.gettext('Remove') == 'Supprimer'
        ... assert translator.gettext('month_01') == 'Janvier'
        >>> translator = get_translator('en')
        ... assert translator.gettext('Remove') == 'Remove'
        ... assert translator.gettext('month_01') == 'January'

    """
    # get possible fallback languages
    try:
        langs = get_lang() or []
    except TypeError:
        # this occurs when Pylons is available and we are not in a valid thread
        langs = []

    # insert lang if provided
    if lang and lang not in langs:
        langs.insert(0, lang)

    if not langs:
        langs = ['en']

    # get the first available catalog
    for lang in langs:
        filename = os.path.join(i18n_path, lang, 'LC_MESSAGES','formalchemy.mo')
        if os.path.isfile(filename):
            translations_path = os.path.join(i18n_path, lang, 'LC_MESSAGES','formalchemy.mo')
            return GNUTranslations(open(translations_path, 'rb'))

    # dummy translator
    return _Translator()

def _(value):
    """dummy 'translator' to mark translation strings in python code"""
    return value

# month translation
_('Year')
_('Month')
_('Day')
_('month_01')
_('month_02')
_('month_03')
_('month_04')
_('month_05')
_('month_06')
_('month_07')
_('month_08')
_('month_09')
_('month_10')
_('month_11')
_('month_12')

