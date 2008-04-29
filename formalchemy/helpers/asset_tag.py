"""
Asset Tag Helpers

Provides functionality for linking an HTML page together with other assets, such as
images, javascripts, stylesheets, and feeds.
"""
# Last synced with Rails copy at Revision 6057 on Feb 7th, 2007.

import os
import re
import urlparse
import warnings
from tags import *
from routes import request_config

# The absolute path of the WebHelpers javascripts directory
javascript_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'javascripts')

# WebHelpers' built-in javascripts. Note: scriptaculous automatically includes all of its
# supporting .js files
javascript_builtins = ('prototype.js', 'scriptaculous.js')

def auto_discovery_link_tag(source, type='rss', **kwargs):
    """
    Returns a link tag allowing browsers and news readers (that support it) to auto-detect
    an RSS or ATOM feed for current page.

    ``source``
        The URL of the feed. The URL is ultimately prepended with the environment's
        ``SCRIPT_NAME`` (the root path of the web application), unless the URL is
        fully-fledged (e.g. http://example.com).

    ``type``
        The type of feed. Specifying 'rss' or 'atom' automatically translates to a type of
        'application/rss+xml' or 'application/atom+xml', respectively. Otherwise the type
        is used as specified. Defaults to 'rss'.
        
    Examples::

        >>> auto_discovery_link_tag('http://feed.com/feed.xml')
        '<link href="http://feed.com/feed.xml" rel="alternate" title="RSS" type="application/rss+xml" />'

        >>> auto_discovery_link_tag('http://feed.com/feed.xml', type='atom')
        '<link href="http://feed.com/feed.xml" rel="alternate" title="ATOM" type="application/atom+xml" />'

        >>> auto_discovery_link_tag('app.rss', type='atom', title='atom feed')
        '<link href="app.rss" rel="alternate" title="atom feed" type="application/atom+xml" />'

        >>> auto_discovery_link_tag('/app.html', type='text/html')
        '<link href="/app.html" rel="alternate" title="" type="text/html" />'
    """
    title = ''
    if type.lower() in ('rss', 'atom'):
        title = type.upper()
        type = 'application/%s+xml' % type.lower()

    tag_args = dict(rel='alternate', type=type, title=title,
                    href=compute_public_path(source))
    kwargs.pop('href', None)
    kwargs.pop('type', None)
    tag_args.update(kwargs)
    return tag('link', **tag_args)

def image_tag(source, alt=None, size=None, **options):
    """
    Returns an image tag for the specified ``source``.

    ``source``
        The source URL of the image. The URL is prepended with '/images/', unless its full
        path is specified. The URL is ultimately prepended with the environment's
        ``SCRIPT_NAME`` (the root path of the web application), unless the URL is
        fully-fledged (e.g. http://example.com).
    
    ``alt``
        The img's alt tag. Defaults to the source's filename, title cased.

    ``size``
        The img's size, specified in the format "XxY". "30x45" becomes
        width="30", height="45". "x20" becomes height="20".
        
    Examples::

        >>> image_tag('xml.png')
        '<img alt="Xml" src="/images/xml.png" />'

        >>> image_tag('rss.png', 'rss syndication')
        '<img alt="rss syndication" src="/images/rss.png" />'

        >>> image_tag("icon.png", size="16x10", alt="Edit Entry")
        '<img alt="Edit Entry" height="10" src="/images/icon.png" width="16" />'

        >>> image_tag("/icons/icon.gif", size="16x16")
        '<img alt="Icon" height="16" src="/icons/icon.gif" width="16" />'

        >>> image_tag("/icons/icon.gif", size="16x")
        '<img alt="Icon" src="/icons/icon.gif" width="16" />'
    """
    if not os.path.splitext(source)[1]:
        warnings.warn("You've called image_tag with a source that doesn't include an "
                      "extension. Soon image_tag will no longer automatically append "
                      "'.png' to your source. Please call image_path('%s.png') "
                      "instead." % source, DeprecationWarning, 2)
    options['src'] = compute_public_path(source, 'images', 'png')

    if not alt:
        alt = os.path.splitext(os.path.basename(source))[0].title()
    options['alt'] = alt
    
    if size and re.match('^(\d+|)x(\d+|)$', size) and size != 'x':
        width, height = size.split('x')
        if width:
            options['width'] = width
        if height:
            options['height'] = height
        
    return tag('img', **options)

def javascript_include_tag(*sources, **options):
    """
    Returns script include tags for the specified javascript ``sources``.

    Each source's URL path is prepended with '/javascripts/' unless their full path is
    specified. Each source's URL path is ultimately prepended with the environment's
    ``SCRIPT_NAME`` (the root path of the web application), unless the URL path is a
    full-fledged URL (e.g. http://example.com). Sources with no filename extension will be
    appended with the '.js' extension.

    Optionally includes (prepended) WebHelpers' built-in javascripts when passed the
    ``builtins=True`` keyword argument.

    Specify the keyword argument ``defer=True`` to enable the script defer attribute.

    Examples::
    
        >>> print javascript_include_tag(builtins=True)
        <script src="/javascripts/prototype.js" type="text/javascript"></script>
        <script src="/javascripts/scriptaculous.js" type="text/javascript"></script>

        >>> print javascript_include_tag(builtins=True, defer=True)
        <script defer="defer" src="/javascripts/prototype.js" type="text/javascript"></script>
        <script defer="defer" src="/javascripts/scriptaculous.js" type="text/javascript"></script>

        >>> print javascript_include_tag('prototype', '/other-javascripts/util.js')
        <script src="/javascripts/prototype.js" type="text/javascript"></script>
        <script src="/other-javascripts/util.js" type="text/javascript"></script>

        >>> print javascript_include_tag('app', '/test/test.1.js', builtins=True)
        <script src="/javascripts/prototype.js" type="text/javascript"></script>
        <script src="/javascripts/scriptaculous.js" type="text/javascript"></script>
        <script src="/javascripts/app.js" type="text/javascript"></script>
        <script src="/test/test.1.js" type="text/javascript"></script>
    """
    if options.pop('builtins', False):
        sources = javascript_builtins + sources
    if options.get('defer') == True:
        options['defer'] = 'defer'

    tags = []
    for source in sources:
        content_options = dict(type='text/javascript',
                               src=compute_public_path(source, 'javascripts',
                                                       'js'))
        content_options.update(options)
        tags.append(content_tag('script', None, **content_options))
    return '\n'.join(tags)

def stylesheet_link_tag(*sources, **options):
    """
    Returns CSS link tags for the specified stylesheet ``sources``.

    Each source's URL path is prepended with '/stylesheets/' unless their full path is
    specified. Each source's URL path is ultimately prepended with the environment's
    ``SCRIPT_NAME`` (the root path of the web application), unless the URL path is a
    full-fledged URL (e.g. http://example.com). Sources with no filename extension will be
    appended with the '.css' extension.
    
    Examples::

        >>> stylesheet_link_tag('style')
        '<link href="/stylesheets/style.css" media="screen" rel="Stylesheet" type="text/css" />'

        >>> stylesheet_link_tag('dir/file', media='all')
        '<link href="/stylesheets/dir/file.css" media="all" rel="Stylesheet" type="text/css" />'

        >>> stylesheet_link_tag('/dir/file', media='all')
        '<link href="/dir/file.css" media="all" rel="Stylesheet" type="text/css" />'
    """
    tag_options = dict(rel='Stylesheet', type='text/css', media='screen')
    tag_options.update(options)
    tag_options.pop('href', None)

    tags = [tag('link', **dict(href=compute_public_path(source, 'stylesheets', 'css'),
                               **tag_options)) for source in sources]
    return '\n'.join(tags)
    
def compute_public_path(source, root_path=None, ext=None):
    """
    Format the specified source for publishing, via the public directory, if applicable.
    """
    if ext and not os.path.splitext(os.path.basename(source))[1]:
        source = '%s.%s' % (source, ext)

    # Avoid munging fully-fledged URLs, including 'mailto:'
    parsed = urlparse.urlparse(source)
    if not (parsed[0] and (parsed[1] or parsed[2])):
        # Prefix apps deployed under any SCRIPT_NAME path
        if not root_path or source.startswith('/'):
            source = '%s%s' % (get_script_name(), source)
        else:
            source = '%s/%s/%s' % (get_script_name(), root_path, source)
    return source

def get_script_name():
    """
    Determine the current web application's ``SCRIPT_NAME``.
    """
    script_name = ''
    config = request_config()
    if hasattr(config, 'environ'):
        script_name = config.environ.get('SCRIPT_NAME', '')
    return script_name

__all__ = ['javascript_path', 'javascript_builtins', 'auto_discovery_link_tag',
           'image_tag', 'javascript_include_tag', 'stylesheet_link_tag']
