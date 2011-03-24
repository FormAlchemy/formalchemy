# -*- coding: utf-8 -*-
import unittest
from formalchemy.tests import *
from formalchemy.fields import AbstractField, FieldRenderer
from formalchemy.fields import _htmlify, deserialize_once

class TestAbstractField(unittest.TestCase):

    def setUp(self):
        self.fs = FieldSet(User)
        self.f = AbstractField(self.fs, name="field", type=types.String)
        self.f.set(renderer=FieldRenderer)
        self.fs.append(self.f)

    def test_not_implemented(self):
        f = self.f
        self.assertRaises(NotImplementedError, lambda: f.model_value)
        self.assertRaises(NotImplementedError, lambda: f.raw_value)
        self.assertRaises(NotImplementedError, f.render)

    def test_errors(self):
        f = self.f
        self.assertEqual(f.errors, [])

class TestUtils(unittest.TestCase):

    def test_htmlify(self):
        class H(object):
            __html__ = ''
            def __repr__(self): return '-'
        self.assertEqual(_htmlify(H()), '-')

        class H(object):
            def __html__(self): return 'html'
            def __repr__(self): return '-'
        self.assertEqual(_htmlify(H()), 'html')

    def test_deserialize_once(self):
        class H(object):
            value = 'foo'
            @deserialize_once
            def deserialize(self):
                return self.value
        h = H()
        self.assertEqual(h.deserialize(), 'foo')
        h.value = 'bar'
        self.assertEqual(h.deserialize(), 'foo')
