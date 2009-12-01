"""
A small module to wrap WebHelpers in FormAlchemy.
"""
from webhelpers.html.tags import text
from webhelpers.html.tags import hidden
from webhelpers.html.tags import password
from webhelpers.html.tags import textarea
from webhelpers.html.tags import checkbox
from webhelpers.html.tags import radio
from webhelpers.html import tags
from webhelpers.html import HTML, literal

def html_escape(s):
    return HTML(s)

escape_once = html_escape

def content_tag(name, content, **options):
    """
    Create a tag with content

    Takes the same keyword args as ``tag``

    Examples::

        >>> print content_tag("p", "Hello world!")
        <p>Hello world!</p>
        >>> print content_tag("div", content_tag("p", "Hello world!"), class_="strong")
        <div class="strong"><p>Hello world!</p></div>
    """
    if content is None:
        content = ''
    tag = HTML.tag(name, _closed=False, **options) + HTML(content) + literal('</%s>' % name)
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
    _update_fa(options, name)
    return text(name, value=value, **options)

def password_field(name="password", value=None, **options):
    """
    Creates a password field

    Takes the same options as text_field
    """
    _update_fa(options, name)
    return password(name, value=value, **options)

def text_area(name, content='', **options):
    """
    Creates a text input area.

    Options:

    * ``size`` - A string specifying the dimensions of the textarea.

    Example::

        >>> print text_area("Body", '', size="25x10")
        <textarea cols="25" id="Body" name="Body" rows="10"></textarea>
    """
    _update_fa(options, name)
    if 'size' in options:
        options["cols"], options["rows"] = options["size"].split("x")
        del options['size']
    return textarea(name, content=content, **options)

def check_box(name, value="1", checked=False, **options):
    """
    Creates a check box.
    """
    _update_fa(options, name)
    if checked:
        options["checked"] = "checked"
    return tags.checkbox(name, value=value, **options)

def hidden_field(name, value=None, **options):
    """
    Creates a hidden field.

    Takes the same options as text_field
    """
    _update_fa(options, name)
    return tags.hidden(name, value=value, **options)

def file_field(name, value=None, **options):
    """
    Creates a file upload field.

    If you are using file uploads then you will also need to set the multipart option for the form.

    Example::

        >>> print file_field('myfile')
        <input id="myfile" name="myfile" type="file" />
    """
    _update_fa(options, name)
    return tags.file(name, value=value, type="file", **options)

def radio_button(name, *args, **options):
    _update_fa(options, name)
    return radio(name, *args, **options)

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

        >>> print tag("br")
        <br />
        >>> print tag("br", True)
        <br>
        >>> print tag("input", type="text")
        <input type="text" />
        >>> print tag("input", type='text', disabled='disabled')
        <input disabled="disabled" type="text" />
    """
    return HTML.tag(name, _closed=not open, **options)

def label(value, **kwargs):
    """
    Return a label tag

        >>> print label('My label', for_='fieldname')
        <label for="fieldname">My label</label>

    """
    if 'for_' in kwargs:
        kwargs['for'] = kwargs.pop('for_')
    return tag('label', open=True, **kwargs) + literal(value) + literal('</label>')

def select(name, selected, select_options, **attrs):
    """
    Creates a dropdown selection box::

    <select id="people" name="people">
    <option value="George">George</option>
    </select>

    """
    if 'options' in attrs:
        del attrs['options']
    if select_options and isinstance(select_options[0], (list, tuple)):
        select_options = [(v, k) for k, v in select_options]
    _update_fa(attrs, name)
    return tags.select(name, selected, select_options, **attrs)

def options_for_select(container, selected=None):
    import warnings
    warnings.warn(DeprecationWarning('options_for_select will be removed in FormAlchemy 2.5'))
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

def _update_fa(attrs, name):
    if 'id' not in attrs:
        attrs['id'] = name
    if 'options' in attrs:
        del attrs['options']

if __name__=="__main__":
    import doctest
    doctest.testmod()
