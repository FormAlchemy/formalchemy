# -*- coding: utf-8 -*-
from formalchemy.tests import *
from formalchemy.fatypes import *
from formalchemy import tests
from webtest import SeleniumApp, selenium

def test_render():
    """
    >>> html5_test_fieldset = FieldSet(Three)
    >>> print html5_test_fieldset.foo.url().render()
    <input id="Three--foo" name="Three--foo" type="url" />

    >>> print html5_test_fieldset.foo.email().render()
    <input id="Three--foo" name="Three--foo" type="email" />

    >>> print html5_test_fieldset.foo.range(min_=2, max_=10, step=5).render()
    <input id="Three--foo" max="10" min="2" name="Three--foo" step="5" type="range" />

    >>> print html5_test_fieldset.foo.number(min_=2, max_=10, step=5).render()
    <input id="Three--foo" max="10" min="2" name="Three--foo" step="5" type="number" />

    >>> print html5_test_fieldset.foo.time().render()
    <input id="Three--foo" name="Three--foo" type="time" />

    >>> print html5_test_fieldset.foo.date().render()
    <input id="Three--foo" name="Three--foo" type="date" />

    >>> print html5_test_fieldset.foo.datetime().render()
    <input id="Three--foo" name="Three--foo" type="datetime" />

    >>> print html5_test_fieldset.foo.datetime_local().render()
    <input id="Three--foo" name="Three--foo" type="date" />

    >>> print html5_test_fieldset.foo.week().render()
    <input id="Three--foo" name="Three--foo" type="week" />

    >>> print html5_test_fieldset.foo.month().render()
    <input id="Three--foo" name="Three--foo" type="month" />

    >>> print html5_test_fieldset.foo.color().render()
    <input id="Three--foo" name="Three--foo" type="color" />
    """

class HTML5(Base):
    __tablename__ = 'html5'
    id = Column('id', Integer, primary_key=True)
    date = Column(HTML5Date, nullable=True)
    time = Column(HTML5Time, nullable=True)
    datetime = Column(HTML5DateTime, nullable=True)
    color = Column(HTML5Color, nullable=True)

@selenium
class TestDateTime(unittest.TestCase):

    def setUp(self):
        self.app = SeleniumApp(application(HTML5))

    def test_render(self):
        resp = self.app.get('/')
        form = resp.form
        form['HTML5--date'] = '2011-01-1'
        form['HTML5--time'] = '12:10'
        form['HTML5--datetime'] = '2011-01-1T10:11Z'
        form['HTML5--color'] = '#fff'
        resp = form.submit()
        resp.mustcontain('OK')
        resp.mustcontain('2011-01-01 10:11:00')

    def tearDown(self):
        self.app.close()

