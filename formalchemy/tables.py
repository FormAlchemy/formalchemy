# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import helpers as h

import base, utils
from forms import FieldSet

__all__ = ["Table", "TableConcat", "TableCollection"]

class Th(object):
    """The `Th` class.

    This class is responsible for rendering a '<th></th>' tag.

    """

    def th(self, colname):
        alias = self._render_options.get('alias', {}).get(colname, colname)
        return h.content_tag("th", self.prettify(alias))

class Td(object):
    """The `Td` class.

    This class is responsible for rendering a '<td></td>' tag.

    """
    def td(self, attr):
        value = attr.value_str()

        display = self._render_options.get("display", {}).get(attr.name)
        if callable(display):
            return h.content_tag("td", display(self.model))

        if value is None or callable(value):
            value = h.content_tag("em", self.prettify("not available."))
        return h.content_tag("td", value)

class Caption(object):
    """The `Caption` class.

    This class is responsible for rendering a caption for a table.

    """
    def caption(self):
        caption = self._render_options.get('caption', True)
        numbering = self._render_options.get('collection_size', True)

        if caption:
            if isinstance(caption, basestring):
                caption_txt = caption
            else:
                caption_txt = "%s" % self.model.__class__.__name__

        if numbering and hasattr(self, "collection"):
            caption_txt += " (%s)" % len(self.collection)

        return h.content_tag('caption', self.prettify(caption_txt))

class Table(base.ModelRender, Caption, Th, Td):
    """The `Table` class.

    This class is responsible for rendering a table from a single model.

    """
    
    def prettify(self, text):
        return self._render_options.get('prettify', base.prettify)(text)
    
    def tbody(self):
        # Make the table's body.
        tbody = []
        for attr in self._get_attrs(**self._render_options):
            tr = []
            tr.append(self.th(attr.name))
            tr.append(self.td(attr))
            tr = utils.wrap("<tr>", "\n".join(tr), "</tr>")
            tbody.append(tr)
        tbody = utils.wrap("<tbody>", "\n".join(tbody), "</tbody>")
        return tbody

    def render(self, **options):
        self._render_options = options

        table = []

        # Make the table's caption.
        caption = self._render_options.get('caption', True)
        if caption:
            table.append(self.caption())

        # Make the table's body.
        tbody = self.tbody()
        table.append(tbody)

        return utils.wrap("<table>", "\n".join(table), "</table>")

class TableCollection(Caption, Th, Td):
    """The `TableCollection` class.

    This class is responsible for rendering a table from a collection of models.

    """
    def __init__(self, collection):
        if not isinstance(collection, (list, tuple)):
            raise Exception('invalid collection %r' % (collection,))
        self.collection = collection
        self.model = None

    def prettify(self, text):
        return self._render_options.get('prettify', base.prettify)(text)
    
    def render(self, **options):
        self._render_options = options
        table = []

        # Make the table's caption.
        caption = self._render_options.get('caption', True)
        if caption:
            table.append(self.caption())

        # Make the table's head.
        thead = []
        tr = []
        mr = base.ModelRender(self.collection[0])
        attrs = mr._get_attrs(**self._render_options)
        for attr in attrs:
            tr.append(self.th(attr.name))
        tr = utils.wrap("<tr>", "\n".join(tr), "</tr>")
        thead.append(tr)

        thead = utils.wrap("<thead>", "\n".join(thead), "</thead>")
        table.append(thead)

        # Make the table's body.
        tbody = []
        for model in self.collection:
            mr.rebind(model)
            self.model = model
            tr = []
            for attr in attrs:
                tr.append(self.td(attr))
            tr = utils.wrap("<tr>", "\n".join(tr), "</tr>")
            tbody.append(tr)
        tbody = utils.wrap("<tbody>", "\n".join(tbody), "</tbody>")
        table.append(tbody)

        return utils.wrap("<table>", "\n".join(table), "</table>")

class TableConcat(Caption):
    """The `TableConcat` class.

    This class is responsible for concatenating different kinds of models in a
    single table. Takes an optional `caption` keyword argument for the table's
    caption. This could be a given string or a model from which the caption
    should be generated from.

    Keyword arguments:
      * `models=[]` - A list of models to render or a paired (model, keyword options): `[client, (address, {'pk':False, 'fk':True})]`.

    <table>
      <caption>Optional caption</caption>
      <tbody>
        # `client` rows
        <th>Name</th><td>Mr Foo</td>
        ...
      </tbody>
      <tbody>
        # `address` rows
        <th>Street</th><td>Foo avenue</td>
        ...
      </tbody>
    </table>

    """
    
    def __init__(self, models=[]):
        self.options = Options()
        self.models = models

    def render(self, caption=False):
        """ Return a rendered table from the given models.

        `caption=False` - A string or one of the models in the model list to render from which caption will be generated from.

        """

        table = []

        # Make the table's body.
        caption_txt = ""
        tbody = []
        for i in self.models:
            if isinstance(i, (list, tuple)):
                model = i[0]
                opts = i[1]
            else:
                model = i
                opts = {}
            t = Table(bind=model)
            t.configure(**opts)
            t._render_options = t.new_options(caption=caption)

            # Do caption rendering
            if caption and not caption_txt:
                if isinstance(caption, basestring) or caption is model:
                    caption_txt = t.caption()
                    table.append(caption_txt)

            # Render the body
            html = t.tbody()
            tbody.append(html)
        table.append("\n".join(tbody))

        return utils.wrap("<table>", "\n".join(table), "</table>")
