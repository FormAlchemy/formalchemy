# -*- coding: utf-8 -*-
import cgi
import copy
from UserDict import DictMixin
from webob.multidict import MultiDict

class UnicodeMultiDict(DictMixin):
    """
    A MultiDict wrapper that decodes returned values to unicode on the
    fly. Decoding is not applied to assigned values.

    The key/value contents are assumed to be ``str``/``strs`` or
    ``str``/``FieldStorages`` (as is returned by the ``paste.request.parse_``
    functions).

    Can optionally also decode keys when the ``decode_keys`` argument is
    True.

    ``FieldStorage`` instances are cloned, and the clone's ``filename``
    variable is decoded. Its ``name`` variable is decoded when ``decode_keys``
    is enabled.

    """
    def __init__(self, multi, encoding=None, errors='strict',
                 decode_keys=False):
        self.multi = multi
        if encoding is None:
            encoding = sys.getdefaultencoding()
        self.encoding = encoding
        self.errors = errors
        self.decode_keys = decode_keys

    def _decode_key(self, key):
        if self.decode_keys:
            try:
                key = key.decode(self.encoding, self.errors)
            except AttributeError:
                pass
        return key

    def _encode_key(self, key):
        if self.decode_keys and isinstance(key, unicode):
            return key.encode(self.encoding, self.errors)
        return key

    def _decode_value(self, value):
        """
        Decode the specified value to unicode. Assumes value is a ``str`` or
        `FieldStorage`` object.

        ``FieldStorage`` objects are specially handled.
        """
        if isinstance(value, cgi.FieldStorage):
            # decode FieldStorage's field name and filename
            value = copy.copy(value)
            if self.decode_keys:
                if not isinstance(value.name, unicode):
                    value.name = value.name.decode(self.encoding, self.errors)
            if value.filename:
                if not isinstance(value.filename, unicode):
                    value.filename = value.filename.decode(self.encoding,
                                                           self.errors)
        elif not isinstance(value, unicode):
            try:
                value = value.decode(self.encoding, self.errors)
            except AttributeError:
                pass
        return value

    def _encode_value(self, value):
        if isinstance(value, unicode):
            value = value.encode(self.encoding, self.errors)
        return value

    def __getitem__(self, key):
        return self._decode_value(self.multi.__getitem__(self._encode_key(key)))

    def __setitem__(self, key, value):
        self.multi.__setitem__(self._encode_key(key), self._encode_value(value))

    def add(self, key, value):
        """
        Add the key and value, not overwriting any previous value.
        """
        self.multi.add(self._encode_key(key), self._encode_value(value))

    def getall(self, key):
        """
        Return a list of all values matching the key (may be an empty list)
        """
        return map(self._decode_value, self.multi.getall(self._encode_key(key)))

    def getone(self, key):
        """
        Get one value matching the key, raising a KeyError if multiple
        values were found.
        """
        return self._decode_value(self.multi.getone(self._encode_key(key)))

    def mixed(self):
        """
        Returns a dictionary where the values are either single
        values, or a list of values when a key/value appears more than
        once in this dictionary.  This is similar to the kind of
        dictionary often used to represent the variables in a web
        request.
        """
        unicode_mixed = {}
        for key, value in self.multi.mixed().iteritems():
            if isinstance(value, list):
                value = [self._decode_value(value) for value in value]
            else:
                value = self._decode_value(value)
            unicode_mixed[self._decode_key(key)] = value
        return unicode_mixed

    def dict_of_lists(self):
        """
        Returns a dictionary where each key is associated with a
        list of values.
        """
        unicode_dict = {}
        for key, value in self.multi.dict_of_lists().iteritems():
            value = [self._decode_value(value) for value in value]
            unicode_dict[self._decode_key(key)] = value
        return unicode_dict

    def __delitem__(self, key):
        self.multi.__delitem__(self._encode_key(key))

    def __contains__(self, key):
        return self.multi.__contains__(self._encode_key(key))

    has_key = __contains__

    def clear(self):
        self.multi.clear()

    def copy(self):
        return UnicodeMultiDict(self.multi.copy(), self.encoding, self.errors)

    def setdefault(self, key, default=None):
        return self._decode_value(
            self.multi.setdefault(self._encode_key(key),
                                  self._encode_value(default)))

    def pop(self, key, *args):
        return self._decode_value(self.multi.pop(self._encode_key(key), *args))

    def popitem(self):
        k, v = self.multi.popitem()
        return (self._decode_key(k), self._decode_value(v))

    def __repr__(self):
        items = map('(%r, %r)'.__mod__, _hide_passwd(self.iteritems()))
        return '%s([%s])' % (self.__class__.__name__, ', '.join(items))

    def __len__(self):
        return self.multi.__len__()

    ##
    ## All the iteration:
    ##

    def keys(self):
        return [self._decode_key(k) for k in self.multi.iterkeys()]

    def iterkeys(self):
        for k in self.multi.iterkeys():
            yield self._decode_key(k)

    __iter__ = iterkeys

    def items(self):
        return [(self._decode_key(k), self._decode_value(v))
                for k, v in self.multi.iteritems()]

    def iteritems(self):
        for k, v in self.multi.iteritems():
            yield (self._decode_key(k), self._decode_value(v))

    def values(self):
        return [self._decode_value(v) for v in self.multi.itervalues()]

    def itervalues(self):
        for v in self.multi.itervalues():
            yield self._decode_value(v)

def _hide_passwd(items):
    for k, v in items:
        if ('password' in k
            or 'passwd' in k
            or 'pwd' in k
        ):
            yield k, '******'
        else:
            yield k, v
