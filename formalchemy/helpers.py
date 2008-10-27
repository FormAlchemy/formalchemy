"""
A small module to remove the WebHelpers dependency in FormAlchemy.

Copyright 2007 Adam Gomaa - MIT License
http://www.opensource.org/licenses/mit-license.php


"""

import cgi, re

def normalize_filename(filename):
    """generate a clean filename::

        >>> print normalize_filename(r'c:\\Program Files\My file.png')
        My_file.png

        >>> print normalize_filename(r'a/b/c/My_file.png')
        My_file.png

    """
    if '\\' in filename:
        filename = filename.split('\\')[-1]
    if '/' in filename:
        filename = filename.split('/')[-1]
    if ' ' in filename:
        filename = filename.replace(' ', '_')
    return filename

# Flag to indcate whether XHTML-style empty tags (< />) should be used.
XHTML = True

def html_escape(s):
    """HTML-escape a string or object

    This converts any non-string objects passed into it to strings
    (actually, using ``unicode()``).  All values returned are
    non-unicode strings (using ``&#num;`` entities for all non-ASCII
    characters).

    None is treated specially, and returns the empty string.
    """
    if s is None:
        return ''
    if not isinstance(s, basestring):
        if hasattr(s, '__unicode__'):
            s = unicode(s)
        else:
            s = str(s)
    s = cgi.escape(s, True)
    if isinstance(s, unicode):
        s = s.encode('ascii', 'xmlcharrefreplace')
    return s

def escape_once(html):
    """Escapes a given string without affecting existing escaped entities.

    >>> escape_once("1 < 2 &amp; 3")
    '1 &lt; 2 &amp; 3'
    """
    return fix_double_escape(html_escape(html))

def fix_double_escape(escaped):
    """Fix double-escaped entities, such as &amp;amp;, &amp;#123;, etc"""
    return re.sub(r'&amp;([a-z]+|(#\d+));', r'&\1;', escaped)

def convert_booleans(options):
    for attr in ['disabled', 'readonly', 'multiple']:
        boolean_attribute(options, attr)
    return options

def boolean_attribute(options, attribute):
    if options.get(attribute):
        options[attribute] = attribute
    elif options.has_key(attribute):
        del options[attribute]

def strip_unders(options):
    for x, y in options.items():
        if x.endswith('_'):
            options[x[:-1]] = y
            del options[x]

def content_tag(name, content, **options):
    """
    Create a tag with content
    
    Takes the same keyword args as ``tag``
    
    Examples::
    
        >>> content_tag("p", "Hello world!")
        '<p>Hello world!</p>'
        >>> content_tag("div", content_tag("p", "Hello world!"), class_="strong")
        '<div class="strong"><p>Hello world!</p></div>'
    """
    if content is None:
        content = ''
    tag = '<%s%s>%s</%s>' % (name, (options and tag_options(**options)) or '', content, name)
    return tag

def text_field(name, value=None, **options):
    """
    Creates a standard text field.
    
    ``value`` is a string, the content of the text field
    
    Options:
    
    * ``disabled`` - If set to True, the user will not be able to use this input.
    * ``size`` - The number of visible characters that will fit in the input.
    * ``maxlength`` - The maximum number of characters that the browser will allow the user to enter.
    
    Remaining keyword options will be standard HTML options for the tag.
    """
    o = {'type': 'text', 'name_': name, 'id': name, 'value': value}
    o.update(options)
    return tag("input", **o)

def password_field(name="password", value=None, **options):
    """
    Creates a password field
    
    Takes the same options as text_field
    """
    return text_field(name, value, type="password", **options)

def text_area(name, content='', **options):
    """
    Creates a text input area.
    
    Options:
    
    * ``size`` - A string specifying the dimensions of the textarea.
    
    Example::
    
        >>> text_area("body", '', size="25x10")
        '<textarea cols="25" id="body" name="body" rows="10"></textarea>'
    """
    if 'size' in options:
        options["cols"], options["rows"] = options["size"].split("x")
        del options['size']
    o = {'name_': name, 'id': name}
    o.update(options)
    return content_tag("textarea", content, **o)

def check_box(name, value="1", checked=False, **options):
    """
    Creates a check box.
    """
    o = {'type': 'checkbox', 'name_': name, 'id': name, 'value': value}
    o.update(options)
    if checked:
        o["checked"] = "checked"
    return tag("input", **o)

def hidden_field(name, value=None, **options):
    """
    Creates a hidden field.
    
    Takes the same options as text_field
    """
    return text_field(name, value, type="hidden", **options)

def file_field(name, value=None, **options):
    """
    Creates a file upload field.
    
    If you are using file uploads then you will also need to set the multipart option for the form.

    Example::

        >>> file_field('myfile')
        '<input id="myfile" name="myfile" type="file" />'
    """
    return text_field(name, value=value, type="file", **options)

def radio_button(name, value, checked=False, **options):
    """Creates a radio button.
    
    The id of the radio button will be set to the name + value with a _ in
    between to ensure its uniqueness.
    """
    pretty_tag_value = re.sub(r'\s', "_", '%s' % value)
    pretty_tag_value = re.sub(r'(?!-)\W', "", pretty_tag_value).lower()
    html_options = {'type': 'radio', 'name_': name, 'id': '%s_%s' % (name, pretty_tag_value), 'value': value}
    html_options.update(options)
    if checked:
        html_options["checked"] = "checked"
    return tag("input", **html_options)

def tag_options(**options):
    strip_unders(options)
    if 'options' in options:
        del options['options']
    cleaned_options = convert_booleans(dict([(x, y) for x, y in options.iteritems() if y is not None]))
    optionlist = ['%s="%s"' % (x, escape_once(y)) for x, y in cleaned_options.iteritems()]
    optionlist.sort()
    if optionlist:
        return ' ' + ' '.join(optionlist)
    else:
        return ''

def tag(name, open=False, **options):
    """
    Returns an XHTML compliant tag of type ``name``.
    
    ``open``
        Set to True if the tag should remain open
    
    All additional keyword args become attribute/value's for the tag. To pass in Python
    reserved words, append _ to the name of the key. For attributes with no value (such as
    disabled and readonly), a value of True is permitted.
    
    Examples::
    
        >>> tag("br")
        '<br />'
        >>> tag("br", True)
        '<br>'
        >>> tag("input", type="text")
        '<input type="text" />'
        >>> tag("input", type='text', disabled=True)
        '<input disabled="disabled" type="text" />'
    """
    tag = '<%s%s%s' % (name, (options and tag_options(**options)) or '', (open and '>') or ' />')
    return tag

def label(value, **kwargs):
    """
    Return a label tag

        >>> print label('My label', for_='fieldname')
        <label for="fieldname">My label</label>

    """
    if 'for_' in kwargs:
        kwargs['for'] = kwargs.pop('for_')
    return tag('label', open=True, **kwargs) + value + '</label>'

def select(name, option_tags='', **options):
    """
    Creates a dropdown selection box
    
    ``option_tags`` is a string containing the option tags for the select box::

        >>> select("people", "<option>George</option>")
        '<select id="people" name="people"><option>George</option></select>'
    
    Options:
    
    * ``multiple`` - If set to true the selection will allow multiple choices.
    
    """
    o = { 'name_': name, 'id': name }
    o.update(options)
    return content_tag("select", option_tags, **o)

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
        
        if value in selected:
            options.append('<option value="%s" selected="selected">%s</option>' % (v, n))
        else :
            options.append('<option value="%s">%s</option>' % (v, n))
    return "\n".join(options)

if __name__=="__main__":
    import doctest
    doctest.testmod()
