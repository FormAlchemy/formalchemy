# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h

import formalchemy.base as base
import formalchemy.utils as utils

__all__ = ["TableItem", "TableCollection", "TableItemConcat"]

class TableCaption(base.BaseModelRender):
    """The `TableCaption` class.

    This class is responsible for rendering a caption for a table.

    """

    def render(self, **options):
        super(TableCaption, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        caption = opts.pop('caption_item', None)
        if isinstance(caption, basestring):
            caption_txt = h.content_tag('caption', self.prettify(caption))
        elif caption is None:
            caption_txt = "%s details" % self._model.__class__.__name__
            caption_txt = h.content_tag('caption', self.prettify(caption_txt))

        return caption_txt

class TableHead(base.BaseColumnRender):
    """The `TableHead` class.

    This class is responsible for rendering a single table head cell '<th>'.

    """

    def render(self, **options):
        super(TableHead, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        self.set_prettify(opts.get('prettify'))
        alias = opts.get('alias', {}).get(self._column, self._column)

        return h.content_tag("th", self.prettify(alias))

class TableData(base.BaseColumnRender):
    """The `TableData` class.

    This class is responsible for rendering a single table data cell '<td>'.

    """

    def render(self, **options):
        super(TableData, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        value = getattr(self._model, self._column)

        display = opts.get("display", {}).get(self._column)
        if callable(display):
            return h.content_tag("td", display(self._model))

        value = getattr(self._model, self._column)
        if isinstance(value, bool):
            value = h.content_tag("em", value)
        elif value is None:
            value = h.content_tag("em", self.prettify("not available."))
        return h.content_tag("td", value)

class TableTHead(base.BaseModelRender):
    """The `TableTHead` class.

    This class is responsible for rendering a table's header row:

    <tr>
      <th>Name</th>
      <th>Email</th>
      <th>Phone</th>
    </tr>

    """

    def render(self, **options):
        super(TableTHead, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        row = []
        for col in self.get_colnames(**opts):
            th = TableHead(column=col, bind=self._model)
            th.reconfigure(**opts)
            row.append(th.render())
        row = utils.wrap("<tr>", "\n".join(row), "</tr>")

        return utils.wrap("<thead>", row, "</thead>")

class TableRowColumn(base.BaseColumnRender):
    """The `TableRowColumn` class.

    This class is responsible for rendering a table row from a model's column:

    <tr>
      <th>Name</th>
      <td>Mr Foo</td>
    </tr>

    """

    def render(self, **options):
        super(TableRowColumn, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        th = TableHead(bind=self._model, column=self._column)
        th.reconfigure(**opts)
        row = th.render()

        td = TableData(bind=self._model, column=self._column)
        td.reconfigure(**opts)
        row += td.render()

        return h.content_tag("tr", row)

class TableRowItem(base.BaseModelRender):
    """The `TableRowItem` class.

    This class is responsible for rendering a table row from a model:

    <tr>
      <td>Mr Foo</td>
      <td>foo@bar.com</td>
      <td>555-1234</td>
    </tr>

    """

    def render(self, **options):
        super(TableRowItem, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        row = []
        for col in self.get_colnames(**opts):
            td = TableData(bind=self._model, column=col)
            td.reconfigure(**opts)
            row.append(td.render())
        return h.content_tag("tr", "\n".join(row))

class TableBodyCollection(base.BaseCollectionRender):
    """The `TableBodyCollection` class.

    This class is responsible for rendering a table's body from a collection
    of items.

    """

    def render(self, **options):
        super(TableBodyCollection, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        if not self._collection:
            if isinstance(self._model, type): # Not instantiated
                msg = "no %s." % (self._model.__name__)
            else:
                msg = "no %s." % (self._model.__class__.__name__)
            colspan_size = len(self.get_colnames(**opts))
            td = utils.wrap('<td colspan="%s">' % colspan_size, self.prettify(msg), "</td>")
            return utils.wrap("<tbody>", utils.wrap("<tr>", td, "</tr>"), "</tbody>")

        tbody = []
        for item in self._collection:
            tr = TableRowItem(bind=item)
            tr.reconfigure(**opts)
            tbody.append(tr.render())
        return utils.wrap("<tbody>", "\n".join(tbody), "</tbody>")

class TableBodyItem(base.BaseModelRender):
    """The `TableBodyItem` class.

    This class is responsible for rendering a table's body from a single item.

    """

    def render(self, **options):
        super(TableBodyItem, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        # Build the table's body.
        # <tr>
        #   <th>column</th><td>value</td>
        # </tr>
        # ...
        tbody = []
        for col in self.get_colnames(**opts):
            tr = TableRowColumn(bind=self._model, column=col)
            tr.reconfigure(**opts)
            tbody.append(tr.render())

        # Wrap in a tbody.
        return utils.wrap("<tbody>", "\n".join(tbody), "</tbody>")

class TableItem(base.BaseModelRender):
    """The `TableItem` class.

    This class is responsible for rendering a table from a single item.

    """

    def render(self, **options):
        super(TableItem, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        table = []

        # Check for caption
        caption = opts.get('caption_item', True)
        if caption:
            tc = TableCaption(bind=self._model)
            tc.reconfigure(**opts)
            table.append(tc.render())

        tb = TableBodyItem(bind=self._model)
        tb.reconfigure(**opts)
        table.append(tb.render())

        return utils.wrap("<table>", "\n".join(table), "</table>")

class TableCollection(base.BaseCollectionRender):
    """The `TableCollection` class.

    This class is responsible for rendering a table from a collection of items.

    """

    def render(self, **options):
        super(TableCollection, self).render()

        # Merge class level options with given argument options.
        opts = base.FormAlchemyDict(self.get_config())
        opts.configure(**options)

        table = []

        # Check for caption
        caption = opts.get('caption_collection', True)
        if caption:
            tc = TableCaption(bind=self._model)
            tc.reconfigure(**opts)
            table.append(tc.render())

        # Build the table's head.
        th = TableTHead(bind=self._model)
        th.reconfigure(**opts)
        table.append(th.render())

        # Build the table's body.
        tb = TableBodyCollection(bind=self._model, collection=self._collection)
        tb.reconfigure(**opts)
        table.append(tb.render())

        return utils.wrap("<table>", "\n".join(table), "</table>")

class TableItemConcat(base.BaseRender):
    """The `TableItemConcat` class.

    This class is responsible for concatenating table items from multiple
    models. Takes a optional `caption` keyword argument for the table's
    caption. This could be a given string or a model from which the caption
    should be generated from.

    Given a list of multiple models `[client, address]` would generate:

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

    def __init__(self, bind=[]):
        self._bind = bind

    def render(self, caption=None, **options):

        table = []

        if isinstance(caption, basestring):
            caption_txt = h.content_tag('caption', self.prettify(caption))
            table.append(caption_txt)
        elif caption in self._bind:
            tc = TableCaption(bind=caption)
            tc.configure(**options)
            table.append(tc.render())

        for model in self._bind:
            tb = TableBodyItem(bind=model)
            tb.configure(**options)
            table.append(tb.render())

        return utils.wrap("<table>", "\n".join(table), "</table>")
