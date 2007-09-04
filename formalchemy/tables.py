# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import webhelpers as h

import formalchemy.base as base
import formalchemy.utils as utils

__all__ = ["TableItem", "TableCollection"]

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

        return utils.wrap("<th>", self.prettify(alias), "</th>")

class TableData(base.BaseColumnRender):
    """The `TableData` class.

    This class is responsible for rendering a single table data cell '<td>'.

    """

    def render(self, **options):
        super(TableData, self).render()

        value = getattr(self._model, self._column)
        if isinstance(value, bool):
            value = h.content_tag("em", value)
        elif value is None:
            value = h.content_tag("em", self.prettify("not available."))
#        return utils.wrap("<td>", str(value), "</td>")
        return h.content_tag("td", value)

class TableTHead(base.BaseModelRender):
    """The `TableTHead` class.

    This class is responsible for rendering a table's header row.

    """

    def render(self, **options):
        super(TableTHead, self).render()

        row = []
        for col in self.get_colnames(**options):
            th = TableHead(column=col, bind=self._model)
            row.append(th.render(**options))
        row = utils.wrap("<tr>", "\n".join(row), "</tr>")

        return utils.wrap("<thead>", row, "</thead>")

class TableRow(base.BaseModelRender):
    """The `TableRow` class.

    This class is responsible for rendering a table's single row from a
    `model`.

    """

    def render(self, **options):
        super(TableRow, self).render()

        row = []
        for col in self.get_colnames(**options):
            td = TableData(bind=self._model, column=col)
            td.reconfigure()
            row.append(td.render(**options))
        return utils.wrap("<tr>", "\n".join(row), "</tr>")

class TableBody(base.BaseCollectionRender):
    """The `TableBody` class.

    This class is responsible for rendering a table's body from a collection
    of items.

    """

    def render(self, **options):
        super(TableBody, self).render()

        if not self._collection:
            msg = self.prettify("no %s." % self._model.__class__.__name__)
            td = utils.wrap('<td colspan="%s">' % len(self.get_colnames(**options)), msg, "</td>")
            return utils.wrap("<tbody>", utils.wrap("<tr>", td, "</tr>"), "</tbody>")

        tbody = []
        for item in self._collection:
            tr = TableRow(bind=item)
            tr.reconfigure()
            tbody.append(tr.render(**options))
        return utils.wrap("<tbody>", "\n".join(tbody), "</tbody>")

class TableItem(base.BaseModelRender):
    """The `TableItem` class.

    This class is responsible for rendering a table from a single item.

    """

    def render(self, **options):
        super(TableItem, self).render()

        tbody = []
        for col in self.get_colnames(**options):
            row = []
            th = TableHead(bind=self._model, column=col)
            th.reconfigure()
            row.append(th.render(**options))

            td = TableData(bind=self._model, column=col)
            td.reconfigure()
            row.append(td.render(**options))

            tbody.append(utils.wrap("<tr>", "\n".join(row), "</tr>"))

        return utils.wrap("<table>", utils.wrap("<tbody>", "\n".join(tbody), "</tbody>"), "</table>")

class TableCollection(base.BaseCollectionRender):
    """The `TableCollection` class.

    This class is responsible for rendering a table from a collection of items.

    """

    def render(self, **options):
        super(TableCollection, self).render()

        table = []

        th = TableTHead(bind=self._model)
        th.reconfigure()
        table.append(th.render(**options))

        tb = TableBody(bind=self._model, collection=self._collection)
        tb.reconfigure()
        table.append(tb.render(**options))

        return utils.wrap("<table>", "\n".join(table), "</table>")
