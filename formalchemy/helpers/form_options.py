"""
Form Options Helpers
"""
# Last synced with Rails copy at Revision 6057 on Feb 7th, 2007.
# Purposely left out a few redundant options_for_collection stuff.

from util import html_escape

def options_for_select(container, selected=None):
    """
    Creates select options from a container (list, tuple, dict)
    
    Accepts a container (list, tuple, dict) and returns a string of option tags. Given a container where the 
    elements respond to first and last (such as a two-element array), the "lasts" serve as option values and
    the "firsts" as option text. Dicts are turned into this form automatically, so the keys become "firsts" and values
    become lasts. If ``selected`` is specified, the matching "last" or element will get the selected option-tag.
    ``Selected`` may also be an array of values to be selected when using a multiple select.
    
    Examples (call, result)::
    
        >>> options_for_select([["Dollar", "$"], ["Kroner", "DKK"]])
        '<option value="$">Dollar</option>\\n<option value="DKK">Kroner</option>'
        >>> options_for_select([ "VISA", "MasterCard" ], "MasterCard")
        '<option value="VISA">VISA</option>\\n<option value="MasterCard" selected="selected">MasterCard</option>'
        >>> options_for_select(dict(Basic="$20", Plus="$40"), "$40")
        '<option value="$40" selected="selected">Plus</option>\\n<option value="$20">Basic</option>'
        >>> options_for_select([ "VISA", "MasterCard", "Discover" ], ["VISA", "Discover"])
        '<option value="VISA" selected="selected">VISA</option>\\n<option value="MasterCard">MasterCard</option>\\n<option value="Discover" selected="selected">Discover</option>'

    Note: Only the option tags are returned, you have to wrap this call in a regular HTML select tag.
    """
    if hasattr(container, 'values'):
        container = container.items()
    
    if not isinstance(selected, (list, tuple)):
        selected = (selected,)
    
    options = []
    
    for elem in container:
        if isinstance(elem, (list, tuple)):
            name, value = elem
            n = html_escape(name)
            v = html_escape(value)
        else :
            name = value = elem
            n = v = html_escape(elem)
        
        #TODO: run timeit for this against content_tag('option', n, value=v, selected=value in selected)
        if value in selected:
            options.append('<option value="%s" selected="selected">%s</option>' % (v, n))
        else :
            options.append('<option value="%s">%s</option>' % (v, n))
    return "\n".join(options)

def options_for_select_from_objects(container, name_attr, value_attr=None, selected=None):
    """
    Create select options from objects in a container
    
    Returns a string of option tags that have been compiled by iterating over the ``container`` and assigning the
    the result of a call to the ``value_attr`` as the option value and the ``name_attr`` as the option text.
    If ``selected`` is specified, the element returning a match on ``value_attr`` will get the selected option tag.
    
    NOTE: Only the option tags are returned, you have to wrap this call in a regular HTML select tag.
    """
    if value_attr:
        def make_elem(elem):
            return getattr(elem, name_attr), getattr(elem, value_attr)
    else :
        def make_elem(elem):
            return getattr(elem, name_attr)
    
    return options_for_select([make_elem(x) for x in container], selected)

def options_for_select_from_dicts(container, name_key, value_key=None, selected=None):
    """
    Create select options from dicts in a container
    
    Returns a string of option tags that have been compiled by iterating over the ``container`` and assigning the
    the result of a call to the ``value_key`` as the option value and the ``name_attr`` as the option text.
    If ``selected`` is specified, the element returning a match on ``value_key`` will get the selected option tag.
    
    NOTE: Only the option tags are returned, you have to wrap this call in a regular HTML select tag.
    """
    if value_key:
        def make_elem(elem):
            return elem[name_key], elem[value_key]
    else:
        def make_elem(elem):
            return elem[name_key]

    return options_for_select([make_elem(x) for x in container], selected)

__all__ = ['options_for_select', 'options_for_select_from_objects', 'options_for_select_from_dicts']
