"""
A small module to remove the WebHelpers dependency in FormAlchemy.

Copyright 2007 Adam Gomaa - MIT License
http://www.opensource.org/licenses/mit-license.php


"""

# Flag to indcate whether XHTML-style empty tags (< />) should be used.
XHTML = True

def build_attr_string(attrs=None):
    """
    Given a dictionary of attributes, construct a string suitable for
    inclusion in an HTML tag mapping the attributes to their values.

    Because Python's dictionary datatype is used, the order of the
    attributes is not usually predictable; therefore, we run the
    dictionary keys through sorted() first. This means that they'll
    come back in alphabetical order of the attribute names.

    No escaping of either attributes or values is done. TODO: is this
    what FormAlchemy expects?

    >>> build_attr_string()
    ''
    >>> build_attr_string({'foo':'bar'})
    ' foo="bar"'
    >>> build_attr_string({'foo':'bar', 'baz':'fooz'})
    ' baz="fooz" foo="bar"'
    
    
    """
    if attrs is None:
        return ""
    attrs = ['%s="%s"' % (key, attrs[key])
             for key in sorted(attrs.keys()) if attrs[key]]
    if not attrs:
        return ""
    else:
        # Space-separated list of key="value" pairs, with a leading space. 
        return " "+' '.join(attrs)


def content_tag(tag_name, content="", for_="", class_="", type_="", xhtml=None, **kwargs):
    """Given a 'name', create a tag for it, give it 'for' and 'class'
    attributes, and populate it with content.

    >>> content_tag("p")
    '<p />'
    >>> content_tag("p", "foo")
    '<p>foo</p>'
    >>> content_tag("label", "Foo", for_="some_id", class_="bar")
    '<label class="bar" for="some_id">Foo</label>'
    >>> content_tag("input", type_="checkbox", checked="checked")
    '<input checked="checked" type="checkbox" />'
    >>> content_tag("input", type_="checkbox", checked="checked", xhtml=False)
    '<input checked="checked" type="checkbox">'
    
    
    """
    # Handle the xhtml argument.
    if xhtml is None:
        xhtml = XHTML
        
    kwargs.update(
        {"for":for_,
         "class": class_,
         "type": type_,
         })
    # Implicit handling of form fields with "name" but not "id" defined. 
    if "name" in kwargs and not "id" in kwargs:
        kwargs["id"] = kwargs["name"]
    attr_string = build_attr_string(kwargs)
    if content:
        return "<%(tag_name)s%(attr_string)s>%(content)s</%(tag_name)s>" % locals()
    elif xhtml:
        return "<%(tag_name)s%(attr_string)s />" % locals()
    else:
        return "<%(tag_name)s%(attr_string)s>" % locals()



def text_field(name, **kwargs):
    """Return a text input. 

    >>> text_field("foo")
    '<input id="foo" name="foo" type="text" />'
    >>> text_field("foo", value="Test!")
    '<input id="foo" name="foo" type="text" value="Test!" />'
    
    """
    return content_tag("input", name=name, type_="text", **kwargs)

def password_field(name, **kwargs):
    """Return a password field.

    >>> password_field("foo")
    '<input id="foo" name="foo" type="password" />'

    """
    return content_tag("input", type_="password", name=name, **kwargs)

def text_area(name, **kwargs):
    """Return a textarea field.

    >>> text_area("foo")
    '<textarea id="foo" name="foo" />'
    >>> text_area("foo", content="Some Content")
    '<textarea id="foo" name="foo">Some Content</textarea>'
    

    """
    return content_tag("textarea", name=name, **kwargs)

def hidden_field(name, **kwargs):
    """Return a hidden field.

    >>> hidden_field("foo")
    '<input id="foo" name="foo" type="hidden" />'
    >>> hidden_field("foo", value="some_value")
    '<input id="foo" name="foo" type="hidden" value="some_value" />'

    """
    return content_tag("input", type_="hidden", name=name, **kwargs)

def check_box(name, value, checked, **kwargs):
    """Return a checkbox.

    >>> check_box("foo", value="bar", checked=True)
    '<input checked="checked" id="foo" name="foo" type="checkbox" value="bar" />'
    >>> check_box("foo", value="bar", checked=False)
    '<input id="foo" name="foo" type="checkbox" value="bar" />'
    >>> check_box("foo", value="bar", checked="checked")
    '<input checked="checked" id="foo" name="foo" type="checkbox" value="bar" />'
    >>> check_box("foo", value="bar", checked="")
    '<input id="foo" name="foo" type="checkbox" value="bar" />'

    """
    if not isinstance(checked, basestring):
        checked = "checked" if checked else ""
    return content_tag("input", type_="checkbox", name=name,
                       value=value, checked=checked, **kwargs)

def file_field(name, **kwargs):
    """Return a file input.

    >>> file_field("foo")
    '<input id="foo" name="foo" type="file" />'

    """
    return content_tag("input", type_="file", name=name, **kwargs)

def radio_button(name, value,**kwargs):
    """Return a radio button

    >>> radio_button("foo", "bar")
    '<input id="foo" name="foo" type="radio" value="bar" />'

    """
    return content_tag("input", type_="radio", name=name, value=value, **kwargs)

def tag(string):
    """Return an empty closed tag.

    >>> tag("p")
    '<p />'

    """
    return "<%s />" % string

def select(name, options_string, **kwargs):
    """Return a select object.

    >>> print select("foo", options_for_select(['test1', 'test2']))
    <select id="foo" name="foo"><option value="test1">test1</option>
    <option value="test2">test2</option></select>
    

    """
    return content_tag("select", name=name, content=options_string, **kwargs)

def options_for_select(options, selected=''):
    """Return a string of options, suitable for use in a select.

    >>> print options_for_select([["Dollar", "$"], ["Kroner", "DKK"]])
    <option value="$">Dollar</option>
    <option value="DKK">Kroner</option>
    >>> print options_for_select([ "VISA", "MasterCard" ], "MasterCard")
    <option value="VISA">VISA</option>
    <option selected="selected" value="MasterCard">MasterCard</option>
    >>> print options_for_select(dict(Basic="$20", Plus="$40"), "$40")
    <option selected="selected" value="$40">Plus</option>
    <option value="$20">Basic</option>
    >>> print options_for_select([ "VISA", "MasterCard", "Discover" ], ["VISA", "Discover"])
    <option selected="selected" value="VISA">VISA</option>
    <option value="MasterCard">MasterCard</option>
    <option selected="selected" value="Discover">Discover</option>


    The following tests for a bug in which a value that was the subset
    of the 'selected' value would be incorrectly selected.

    >>> print options_for_select(["a", "ab"], "ab")
    <option value="a">a</option>
    <option selected="selected" value="ab">ab</option>

    

    """
    ## Transform a dictionary into a list of [[key, value]].
    if isinstance(options, dict):
        options = [[key, options[key]] for key in options]
    
    ## Transform a list of [content] into a list of [[content,
    # value]].  Check the first element: if it's not a list, we need
    # to copy the content to value for each one.
    if not isinstance(options[0], (tuple, list)):
        options = [[content, content] for content in options]

    if not isinstance(selected,  (tuple, list)):
        # Turn a passed-in string to a list so we can use it in a list
        # comprehension below
        selected = [selected]

    tags = [content_tag(
        "option", content=content, value=value,
        # The Boolean will eval to 0 or 1, so multiplying "selected"
        # by that means that we'll end up with selected="" or
        # selected="selected", respectively. content_tag() will filter
        # the former.
        selected="selected"*bool([
                sel for sel in selected if sel==value]))
            for content, value in options]
    return '\n'.join(tags)

def javascript_tag(content, **kwargs):
    """
    Return a javascript tag, with code escaped in a CDATA section.

    >>> print javascript_tag('window.alert("foo!")')
    <script type="text/javascript">
    // <![CDATA[
    window.alert("foo!")
    // ]]>
    </script>

    """
    return content_tag("script", "\n// <![CDATA[\n%s\n// ]]>\n" % content,
                       type_="text/javascript",**kwargs)

if __name__=="__main__":
    import doctest
    doctest.testmod()
