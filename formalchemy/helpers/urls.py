"""URL Helpers"""
# Last synced with Rails copy at Revision 6070 on Feb 8th, 2007.

import re
import urllib

from routes import url_for, request_config

import tags
from asset_tag import compute_public_path
from javascript import *
from util import html_escape

def get_url(url):
    if callable(url):
        return url()
    else:
        return url

def url(*args, **kargs):
    """
    Lazily evaluates url_for() arguments
    
    Used instead of url_for() for functions so that the function will be evaluated
    in a lazy manner rather than at initial function call.
    """
    args = args
    kargs = kargs
    def call():
        return url_for(*args, **kargs)
    return call

def link_to(name, url='', **html_options):
    """
    Creates a link tag of the given ``name`` using an URL created by the set of ``options``.
    
    See the valid options in the documentation for Routes url_for.
    
    The html_options has three special features. One for creating javascript confirm alerts where if you pass
    ``confirm='Are you sure?'`` , the link will be guarded with a JS popup asking that question. If the user
    accepts, the link is processed, otherwise not.
    
    Another for creating a popup window, which is done by either passing ``popup`` with True or the options
    of the window in Javascript form.
    
    And a third for making the link do a POST request (instead of the regular GET) through a dynamically added
    form element that is instantly submitted. Note that if the user has turned off Javascript, the request will
    fall back on the GET. So its your responsibility to determine what the action should be once it arrives at
    the controller. The POST form is turned on by passing ``post`` as True. Note, it's not possible to use POST
    requests and popup targets at the same time (an exception will be thrown).
    
    Examples::
    
        >> link_to("Delete this page", url(action="destroy", id=4), confirm="Are you sure?")
        >> link_to("Help", url(action="help"), popup=True)
        >> link_to("Busy loop", url(action="busy"), popup=['new_window', 'height=300,width=600'])
        >> link_to("Destroy account", url(action="destroy"), confirm="Are you sure?", method='delete')
    """
    if html_options:
        html_options = convert_options_to_javascript(**html_options)
        tag_op = tags.tag_options(**html_options)
    else:
        tag_op = ''
    if callable(url):
        url = url()
    else:
        url = html_escape(url)
    return "<a href=\"%s\"%s>%s</a>" % (url, tag_op, name or url)

def button_to(name, url='', **html_options):
    """
    Generates a form containing a sole button that submits to the
    URL given by ``url``.  
    
    Use this method instead of ``link_to`` for actions that do not have the safe HTTP GET semantics
    implied by using a hypertext link.
    
    The parameters are the same as for ``link_to``.  Any ``html_options`` that you pass will be
    applied to the inner ``input`` element.
    In particular, pass
    
        disabled = True/False
    
    as part of ``html_options`` to control whether the button is
    disabled.  The generated form element is given the class
    'button-to', to which you can attach CSS styles for display
    purposes.
    
    The submit button itself will be displayed as an image if you provide both
    ``type`` and ``src`` as followed:

         type='image', src='icon_delete.gif'

    The ``src`` path will be computed as the image_tag() computes it's ``source``
    argument.

    Example 1::
    
        # inside of controller for "feeds"
        >> button_to("Edit", url(action='edit', id=3))
        <form method="POST" action="/feeds/edit/3" class="button-to">
        <div><input value="Edit" type="submit" /></div>
        </form>
    
    Example 2::
    
        >> button_to("Destroy", url(action='destroy', id=3), confirm="Are you sure?", method='DELETE')
        <form method="POST" action="/feeds/destroy/3" class="button-to">
        <div>
            <input type="hidden" name="_method" value="DELETE" />
            <input onclick="return confirm('Are you sure?');" value="Destroy" type="submit" />
        </div>
        </form>

    Example 3::

        # Button as an image.
        >> button_to("Edit", url(action='edit', id=3), type='image', src='icon_delete.gif')
        <form method="POST" action="/feeds/edit/3" class="button-to">
        <div><input alt="Edit" src="/images/icon_delete.gif" type="image" value="Edit" /></div>
        </form>
    
    *NOTE*: This method generates HTML code that represents a form.
    Forms are "block" content, which means that you should not try to
    insert them into your HTML where only inline content is expected.
    For example, you can legally insert a form inside of a ``div`` or
    ``td`` element or in between ``p`` elements, but not in the middle of
    a run of text, nor can you place a form within another form.
    (Bottom line: Always validate your HTML before going public.)    
    """
    if html_options:
        convert_boolean_attributes(html_options, ['disabled'])
    
    method_tag = ''
    method = html_options.pop('method', '')
    if method.upper() in ['PUT', 'DELETE']:
        method_tag = tags.tag('input', type_='hidden', id='_method', name_='_method',
                              value=method)
    
    form_method = (method.upper() == 'GET' and method) or 'POST'
    
    confirm = html_options.get('confirm')
    if confirm:
        del html_options['confirm']
        html_options['onclick'] = "return %s;" % confirm_javascript_function(confirm)
    
    if callable(url):
        ur = url()
        url, name = ur, name or tags.escape_once(ur)
    else:
        url, name = url, name or url
    
    submit_type = html_options.get('type')
    img_source = html_options.get('src')
    if submit_type == 'image' and img_source:
        html_options.update(dict(type=submit_type, value=name,
                                 alt=html_options.get('alt', name)))
        html_options['src'] = compute_public_path(img_source, 'images', 'png')
    else:
        html_options.update(dict(type='submit', value=name))
    
    return """<form method="%s" action="%s" class="button-to"><div>""" % \
        (form_method, tags.escape_once(url)) + method_tag + \
        tags.tag("input", **html_options) + "</div></form>"

def link_to_unless_current(name, url, **html_options):
    """
    Conditionally create a link tag of the given ``name`` using the ``url``
    
    If the current request uri is the same as the link's only the name is returned. This is useful
    for creating link bars where you don't want to link to the page currently being viewed.
    """
    return link_to_unless(current_page(url), name, url, **html_options)

def link_to_unless(condition, name, url, **html_options):
    """
    Conditionally create a link tag of the given ``name`` using the ``url``
    
    If ``condition`` is True only the name is returned.
    """
    if condition:
        return name
    else:
        return link_to(name, url, **html_options)

def link_to_if(condition, name, url, **html_options):
    """
    Conditionally create a link tag of the given ``name`` using the ``url`` 
    
    If ``condition`` is True only the name is returned.
    """
    return link_to_unless(not condition, name, url, **html_options)

def current_page(url):
    """
    Returns true if the current page uri is equivalent to ``url``
    """
    currl = current_url()
    if callable(url):
        return url() == currl
    else:
        return url == currl

def current_url(*args, **kwargs):
    """
    Returns the current page's url.
    """
    config = request_config()
    environ = config.environ
    qs = environ.get('QUERY_STRING', '')
    if qs:
        qs = '?' + qs
    return url_for(*args, **kwargs) + qs

def convert_options_to_javascript(confirm=None, popup=None, post=None, method=None, **html_options):
    if post and not method:
        method = 'POST'
    
    if popup and method:
        raise ValueError("You can't use popup and post in the same link")
    elif confirm and popup:
        oc = "if (%s) { %s };return false;" % (confirm_javascript_function(confirm), 
                                               popup_javascript_function(popup))
    elif confirm and method:
        oc = "if (%s) { %s };return false;" % (confirm_javascript_function(confirm),
                                               method_javascript_function(method))
    elif confirm:
        oc = "return %s;" % confirm_javascript_function(confirm)
    elif method:
        oc = "%sreturn false;" % method_javascript_function(method)
    elif popup:
        oc = popup_javascript_function(popup) + 'return false;'
    else:
        oc = html_options.get('onclick')
    html_options['onclick'] = oc
    return html_options
    
def convert_boolean_attributes(html_options, bool_attrs):
    for attr in bool_attrs:
        if html_options.has_key(attr) and html_options[attr]:
            html_options[attr] = attr
        elif html_options.has_key(attr):
            del html_options[attr]

def confirm_javascript_function(confirm):
    return "confirm('%s')" % escape_javascript(confirm)

def popup_javascript_function(popup):
    if isinstance(popup, list):
        return "window.open(this.href,'%s','%s');" % (popup[0], popup[-1])
    else:
        return "window.open(this.href);"

def method_javascript_function(method):
    submit_function = "var f = document.createElement('form'); f.style.display = 'none'; " + \
        "this.parentNode.appendChild(f); f.method = 'POST'; f.action = this.href;"
    
    if method.upper() != 'POST':
        submit_function += "var m = document.createElement('input'); m.setAttribute('type', 'hidden'); "
        submit_function += "m.setAttribute('name', '_method'); m.setAttribute('value', '%s'); f.appendChild(m);" % method
    
    return submit_function + "f.submit();"


def mail_to(email_address, name=None, cc=None, bcc=None, subject=None, 
    body=None, replace_at=None, replace_dot=None, encode=None, **html_options):
    """
    Creates a link tag for starting an email to the specified 
    ``email_address``, which is also used as the name of the link unless
    ``name`` is specified. Additional HTML options, such as class or id, can be
    passed in the ``html_options`` hash.
    
    You can also make it difficult for spiders to harvest email address by 
    obfuscating them.
    
    Examples::
    
        >>> mail_to("me@domain.com", "My email", encode = "javascript")
        '<script type="text/javascript">\\n//<![CDATA[\\neval(unescape(\\'%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%61%20%68%72%65%66%3d%22%6d%61%69%6c%74%6f%3a%6d%65%40%64%6f%6d%61%69%6e%2e%63%6f%6d%22%3e%4d%79%20%65%6d%61%69%6c%3c%2f%61%3e%27%29%3b\\'))\\n//]]>\\n</script>'
    
        >>> mail_to("me@domain.com", "My email", encode = "hex")
        '<a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;%6d%65@%64%6f%6d%61%69%6e.%63%6f%6d">My email</a>'
    
    You can also specify the cc address, bcc address, subject, and body parts
    of the message header to create a complex e-mail using the corresponding
    ``cc``, ``bcc``, ``subject``, and ``body`` keyword arguments. Each of these
    options are URI escaped and then appended to the ``email_address`` before
    being output. **Be aware that javascript keywords will not be escaped and
    may break this feature when encoding with javascript.**
    
    Examples::
    
        >>> mail_to("me@domain.com", "My email", cc="ccaddress@domain.com", bcc="bccaddress@domain.com", subject="This is an example email", body= "This is the body of the message.")
        '<a href="mailto:me@domain.com?cc=ccaddress%40domain.com&amp;body=This%20is%20the%20body%20of%20the%20message.&amp;subject=This%20is%20an%20example%20email&amp;bcc=bccaddress%40domain.com">My email</a>'
    """
    extras = {}
    for key, option in ('cc', cc), ('bcc', bcc), ('subject', subject), ('body', body):
        if option:
            extras[key] = option
    options_query = urllib.urlencode(extras).replace("+", "%20")
    protocol = 'mailto:'

    email_address_obfuscated = email_address
    if replace_at:
        email_address_obfuscated = email_address_obfuscated.replace('@', replace_at)
    if replace_dot:
        email_address_obfuscated = email_address_obfuscated.replace('.', replace_dot)

    if encode == 'hex':
        email_address_obfuscated = ''.join(['&#%d;' % ord(x) for x in email_address_obfuscated])
        protocol = ''.join(['&#%d;' % ord(x) for x in protocol])

        word_re = re.compile('\w')
        encoded_parts = []
        for x in email_address:
            if word_re.match(x):
                encoded_parts.append('%%%x' % ord(x))
            else:
                encoded_parts.append(x)
        email_address = ''.join(encoded_parts)

    url = protocol + email_address
    if options_query:
        url += '?' + options_query
    html_options['href'] = url

    tag = tags.content_tag('a', name or email_address_obfuscated, **html_options)

    if encode == 'javascript':
        tmp = "document.write('%s');" % tag
        string = ''.join(['%%%x' % ord(x) for x in tmp])
        return javascript_tag("eval(unescape('%s'))" % string)
    else : 
        return tag

def js_obfuscate(data):
    """Obfuscates data in a Javascript tag
    
    Example::
        
        >>> js_obfuscate("<input type='hidden' name='check' value='valid' />")
        '<script type="text/javascript">\\n//<![CDATA[\\neval(unescape(\\'%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%27%3c%69%6e%70%75%74%20%74%79%70%65%3d%27%68%69%64%64%65%6e%27%20%6e%61%6d%65%3d%27%63%68%65%63%6b%27%20%76%61%6c%75%65%3d%27%76%61%6c%69%64%27%20%2f%3e%27%29%3b\\'))\\n//]]>\\n</script>'
    """
    tmp = "document.write('%s');" % data
    string = ''.join(['%%%x' % ord(x) for x in tmp])
    return javascript_tag("eval(unescape('%s'))" % string)

__all__ = ['url', 'link_to', 'button_to', 'link_to_unless_current', 'link_to_unless', 'link_to_if',
           'current_page', 'current_url', 'mail_to', 'js_obfuscate']
