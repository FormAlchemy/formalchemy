# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import helpers as h

import base, utils

from tempita import Template as TempitaTemplate # must import after base


__all__ = ["Table", "TableCollection"]


template_single = r"""
<tbody>
{{for field in table.render_fields.itervalues()}}
  <tr>
    <td class="table_label">{{field.label_text or table.prettify(field.key)}}:</td>
    <td class="table_field">{{field.value_str()}}</td>
  </tr>
{{endfor}}
</tbody>
"""
render_single = TempitaTemplate(template_single, name='template_single_table').substitute

template_collection = r"""
<thead>
  <tr>
    {{for field in collection.render_fields.itervalues()}}
      <th>{{field.label_text or collection.prettify(field.key)}}:</td>
    {{endfor}}
  </tr>
</thead>

<tbody>
{{for row in collection.rows:}}
  {{collection.rebind(row, collection.session)}}
  <tr>
  {{for field in collection.render_fields.itervalues()}}
    <td>{{field.value_str()}}</td>
  {{endfor}}
  </tr>
{{endfor}}
</tbody>
"""
render_collection = TempitaTemplate(template_collection, name='template_collection_table').substitute


class Table(base.ModelRenderer):
    """
    The `Table` class renders tables from a single model, with the field labels
    in column one, and the field values in column two.
    """
    prettify = staticmethod(base.prettify)
    _render = staticmethod(render_single)
    
    def render(self):
        return self._render(table=self)


class TableCollection(base.ModelRenderer):
    """
    The `TableCollection` class renders a table where each row represents a model instance.
    It must be bound to an iterable of instances of the same class.
    """
    prettify = staticmethod(base.prettify)
    _render = staticmethod(render_collection)

    def __init__(self, cls, instances, session=None):
        base.ModelRenderer.__init__(self, cls, session)
        self.rows = instances

    def render(self):
        return self._render(collection=self)
