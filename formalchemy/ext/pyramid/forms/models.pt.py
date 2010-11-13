registry = dict(version=0)
def bind():
    from cPickle import loads as _loads
    _lookup_attr = _loads('cchameleon.core.codegen\nlookup_attr\np1\n.')
    _init_scope = _loads('cchameleon.core.utils\necontext\np1\n.')
    _attrs_4346663184 = _loads('(dp1\n.')
    _attrs_4346662992 = _loads('(dp1\n.')
    _attrs_4346663504 = _loads('(dp1\n.')
    _attrs_4346663376 = _loads('(dp1\n.')
    _attrs_4346663248 = _loads('(dp1\n.')
    _init_stream = _loads('cchameleon.core.generation\ninitialize_stream\np1\n.')
    _attrs_4346663632 = _loads('(dp1\n.')
    _init_default = _loads('cchameleon.core.generation\ninitialize_default\np1\n.')
    _re_amp = _loads("cre\n_compile\np1\n(S'&(?!([A-Za-z]+|#[0-9]+);)'\np2\nI0\ntRp3\n.")
    _init_tal = _loads('cchameleon.core.generation\ninitialize_tal\np1\n.')
    def render(econtext, rcontext=None):
        macros = econtext.get('macros')
        _translate = econtext.get('_translate')
        _slots = econtext.get('_slots')
        target_language = econtext.get('target_language')
        u'_init_stream()'
        (_out, _write, ) = _init_stream()
        u'_init_tal()'
        (_attributes, repeat, ) = _init_tal()
        u'_init_default()'
        _default = _init_default()
        u'None'
        default = None
        u'None'
        _domain = None
        attrs = _attrs_4346662992
        _write(u'<html>\n    ')
        attrs = _attrs_4346663184
        _write(u'<head>\n    </head>\n    ')
        attrs = _attrs_4346663248
        u'models'
        _write(u'<body>\n        ')
        _tmp1 = econtext['models']
        item = None
        (_tmp1, _tmp2, ) = repeat.insert('item', _tmp1)
        for item in _tmp1:
            _tmp2 = (_tmp2 - 1)
            attrs = _attrs_4346663376
            _write(u'<div>\n          ')
            attrs = _attrs_4346663504
            u"''"
            _write(u'<div>\n            ')
            _default.value = default = ''
            u'item'
            _content = item
            attrs = _attrs_4346663632
            u'${item}'
            _write(u'<a')
            _tmp3 = item
            if (_tmp3 is _default):
                _tmp3 = None
            if ((_tmp3 is not None) and (_tmp3 is not False)):
                if (_tmp3.__class__ not in (str, unicode, int, float, )):
                    _tmp3 = unicode(_translate(_tmp3, domain=_domain, mapping=None, target_language=target_language, default=None))
                else:
                    if not isinstance(_tmp3, unicode):
                        _tmp3 = str(_tmp3)
                if ('&' in _tmp3):
                    if (';' in _tmp3):
                        _tmp3 = _re_amp.sub('&amp;', _tmp3)
                    else:
                        _tmp3 = _tmp3.replace('&', '&amp;')
                if ('<' in _tmp3):
                    _tmp3 = _tmp3.replace('<', '&lt;')
                if ('>' in _tmp3):
                    _tmp3 = _tmp3.replace('>', '&gt;')
                if ('"' in _tmp3):
                    _tmp3 = _tmp3.replace('"', '&quot;')
                _write(((' href="' + _tmp3) + '"'))
            u'_content'
            _write('>')
            _tmp3 = _content
            _tmp = _tmp3
            if (_tmp.__class__ not in (str, unicode, int, float, )):
                try:
                    _tmp = _tmp.__html__
                except:
                    _tmp = _translate(_tmp, domain=_domain, mapping=None, target_language=target_language, default=None)
                else:
                    _tmp = _tmp()
                    _write(_tmp)
                    _tmp = None
            if (_tmp is not None):
                if not isinstance(_tmp, unicode):
                    _tmp = str(_tmp)
                if ('&' in _tmp):
                    if (';' in _tmp):
                        _tmp = _re_amp.sub('&amp;', _tmp)
                    else:
                        _tmp = _tmp.replace('&', '&amp;')
                if ('<' in _tmp):
                    _tmp = _tmp.replace('<', '&lt;')
                if ('>' in _tmp):
                    _tmp = _tmp.replace('>', '&gt;')
                _write(_tmp)
            _write(u'</a>\n          </div>\n        </div>')
            if (_tmp2 == 0):
                break
            _write(' ')
        _write(u'\n    </body>\n</html>')
        return _out.getvalue()
    return render

__filename__ = u'/Users/gawel/py/FormAlchemy/formalchemy/ext/pyramid/forms/models.pt'
registry[(None, True, '1488bdb950901f8f258549439ef6661a49aae984')] = bind()
