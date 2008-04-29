"""
Prototype Helpers

Provides a set of helpers for calling Prototype JavaScript functions, 
including functionality to call remote methods using 
`Ajax <http://www.adaptivepath.com/publications/essays/archives/000385.php>`_. 
This means that you can call actions in your controllers without
reloading the page, but still update certain parts of it using
injections into the DOM. The common use case is having a form that adds
a new element to a list without reloading the page.

To be able to use these helpers, you must include the Prototype 
JavaScript framework in your pages.

See `link_to_remote <module-railshelpers.helpers.javascript.html#link_to_function>`_ 
for documentation of options common to all Ajax helpers.

See also `Scriptaculous <module-railshelpers.helpers.scriptaculous.html>`_ for
helpers which work with the Scriptaculous controls and visual effects library.
"""
# Last synced with Rails copy at Revision 6057 on Feb 9th, 2007.

import sys
if sys.version < '2.4':
    from sets import ImmutableSet as frozenset

from javascript import *
from javascript import options_for_javascript
from form_tag import form
from tags import tag, camelize
from urls import get_url

CALLBACKS = frozenset(['uninitialized', 'loading', 'loaded',
                       'interactive', 'complete', 'failure', 'success'] + \
                          [str(x) for x in range(100,599)])
AJAX_OPTIONS = frozenset(['before', 'after', 'condition', 'url',
                          'asynchronous', 'method', 'insertion', 'position',
                          'form', 'with', 'with_', 'update', 'script'] + \
                             list(CALLBACKS))

def link_to_remote(name, options=None, **html_options):
    """
    Links to a remote function
    
    Returns a link to a remote action defined ``dict(url=url())``
    (using the url() format) that's called in the background using 
    XMLHttpRequest. The result of that request can then be inserted into a
    DOM object whose id can be specified with the ``update`` keyword. 
    
    Any keywords given after the second dict argument are considered html options
    and assigned as html attributes/values for the element.
    
    Example::
    
        link_to_remote("Delete this post", dict(update="posts", 
                       url=url(action="destroy", id=post.id)))
    
    You can also specify a dict for ``update`` to allow for easy redirection
    of output to an other DOM element if a server-side error occurs:
    
    Example::

        link_to_remote("Delete this post",
                dict(url=url(action="destroy", id=post.id),
                     update=dict(success="posts", failure="error")))
    
    Optionally, you can use the ``position`` parameter to influence how the
    target DOM element is updated. It must be one of 'before', 'top', 'bottom',
    or 'after'.
    
    By default, these remote requests are processed asynchronous during 
    which various JavaScript callbacks can be triggered (for progress 
    indicators and the likes). All callbacks get access to the 
    ``request`` object, which holds the underlying XMLHttpRequest. 
    
    To access the server response, use ``request.responseText``, to
    find out the HTTP status, use ``request.status``.
    
    Example::

        link_to_remote(word,
                dict(url=url(action="undo", n=word_counter),
                     complete="undoRequestCompleted(request)"))
    
    The callbacks that may be specified are (in order):
    
    ``loading``
        Called when the remote document is being loaded with data by the browser.
    ``loaded``
        Called when the browser has finished loading the remote document.
    ``interactive``
        Called when the user can interact with the remote document, even
        though it has not finished loading.
    ``success``
        Called when the XMLHttpRequest is completed, and the HTTP status
        code is in the 2XX range.
    ``failure``
        Called when the XMLHttpRequest is completed, and the HTTP status code is
        not in the 2XX range.
    ``complete``
        Called when the XMLHttpRequest is complete (fires after success/failure
        if they are present).
                        
    You can further refine ``success`` and ``failure`` by 
    adding additional callbacks for specific status codes.
    
    Example::
    
        link_to_remote(word,
                dict(url=url(action="action"),
                     404="alert('Not found...? Wrong URL...?')",
                     failure="alert('HTTP Error ' + request.status + '!')"))
    
    A status code callback overrides the success/failure handlers if 
    present.
    
    If you for some reason or another need synchronous processing (that'll
    block the browser while the request is happening), you can specify 
    ``type='synchronous'``.
    
    You can customize further browser side call logic by passing in
    JavaScript code snippets via some optional parameters. In their order 
    of use these are:
    
    ``confirm``
        Adds confirmation dialog.
    ``condition``
        Perform remote request conditionally by this expression. Use this to
        describe browser-side conditions when request should not be initiated.
    ``before``
        Called before request is initiated.
    ``after``
        Called immediately after request was initiated and before ``loading``.
    ``submit``
        Specifies the DOM element ID that's used as the parent of the form
        elements. By default this is the current form, but it could just as
        well be the ID of a table row or any other DOM element.    
    """
    if options is None:
        options = {}
    return link_to_function(name, remote_function(**options), **html_options)

def periodically_call_remote(**options):
    """
    Periodically calls a remote function
    
    Periodically calls the specified ``url`` every ``frequency`` seconds
    (default is 10). Usually used to update a specified div ``update``
    with the results of the remote call. The options for specifying the
    target with ``url`` and defining callbacks is the same as `link_to_remote <#link_to_remote>`_.    
    """
    frequency = options.get('frequency') or 10
    code = "new PeriodicalExecuter(function() {%s}, %s)" % (remote_function(**options), frequency)
    return javascript_tag(code)

def form_remote_tag(**options):
    """
    Create a form tag using a remote function to submit the request
    
    Returns a form tag that will submit using XMLHttpRequest in the 
    background instead of the regular reloading POST arrangement. Even 
    though it's using JavaScript to serialize the form elements, the form
    submission will work just like a regular submission as viewed by the
    receiving side. The options for specifying the target with ``url``
    and defining callbacks is the same as `link_to_remote <#link_to_remote>`_.
    
    A "fall-through" target for browsers that doesn't do JavaScript can be
    specified with the ``action/method`` options on ``html``.
    
    Example::

        form_remote_tag(html=dict(action=url(
                                    controller="some", action="place")))
    
    By default the fall-through action is the same as the one specified in 
    the ``url`` (and the default method is ``POST``).
    """
    options['form'] = True
    if 'html' not in options: options['html'] = {}
    options['html']['onsubmit'] = "%s; return false;" % remote_function(**options)
    action = options['html'].get('action', get_url(options['url']))
    options['html']['method'] = options['html'].get('method', 'POST')
    
    return form(action, **options['html'])

def submit_to_remote(name, value, **options):
    """
    A submit button that submits via an XMLHttpRequest call
    
    Returns a button input tag that will submit form using XMLHttpRequest 
    in the background instead of regular reloading POST arrangement. 
    Keyword args are the same as in ``form_remote_tag``.    
    """
    options['with_'] = options.get('form') or 'Form.serialize(this.form)'
    
    options['html'] = options.get('html') or {}
    options['html']['type'] = 'button'
    options['html']['onclick'] = "%s; return false;" % remote_function(**options)
    options['html']['name_'] = name
    options['html']['value'] = '%s' % value
    
    return tag("input", open=False, **options['html'])

def update_element_function(element_id, **options):
    """
    Returns a JavaScript function (or expression) that'll update a DOM 
    element.
    
    ``content``
        The content to use for updating.
    ``action``
        Valid options are 'update' (assumed by default), 'empty', 'remove'
    ``position``
        If the ``action`` is 'update', you can optionally specify one of the
        following positions: 'before', 'top', 'bottom', 'after'.
    
    Example::
    
        <% javascript_tag(update_element_function("products", 
            position='bottom', content="<p>New product!</p>")) %>
    
    This method can also be used in combination with remote method call 
    where the result is evaluated afterwards to cause multiple updates on
    a page. Example::
    
        # Calling view
        <% form_remote_tag(url=url(action="buy"), 
                complete=evaluate_remote_response()) %>
            all the inputs here...
    
        # Controller action
        def buy(self, **params):
            c.product = Product.find(1)
            return render_response('/buy.myt')
    
        # Returning view (buy.myt)
        <% update_element_function(
                "cart", action='update', position='bottom', 
                content="<p>New Product: %s</p>" % c.product.name) %>
        <% update_element_function("status", binding='binding',
                content="You've bought a new product!") %>
    """
    content = escape_javascript(options.get('content', ''))
    opval = options.get('action', 'update')
    if opval == 'update':
        if options.get('position'):
            jsf = "new Insertion.%s('%s','%s')" % (camelize(options['position']), element_id, content)
        else:
            jsf = "$('%s').innerHTML = '%s'" % (element_id, content)
    elif opval == 'empty':
        jsf = "$('%s').innerHTML = ''" % element_id
    elif opval == 'remove':
        jsf = "Element.remove('%s')" % element_id
    else:
        raise ValueError("Invalid action, choose one of update, remove, or empty")
    
    jsf += ";\n"
    if options.get('binding'):
        return jsf + options['binding']
    else:
        return jsf

def evaluate_remote_response():
    """
    Returns a Javascript function that evals a request response
    
    Returns 'eval(request.responseText)' which is the JavaScript function
    that ``form_remote_tag`` can call in *complete* to evaluate a multiple
    update return document using ``update_element_function`` calls.    
    """
    return "eval(request.responseText)"

def remote_function(**options):
    """
    Returns the JavaScript needed for a remote function.
    
    Takes the same options that can be passed as ``options`` to
    `link_to_remote <#link_to_remote>`_.
    
    Example::
    
        <select id="options" onchange="<% remote_function(update="options", 
                url=url(action='update_options')) %>">
            <option value="0">Hello</option>
            <option value="1">World</option>
        </select>    
    """
    javascript_options = options_for_ajax(options)
    
    update = ''
    if options.get('update') and isinstance(options['update'], dict):
        update = []
        if options['update'].has_key('success'): 
            update.append("success:'%s'" % options['update']['success'])
        if options['update'].has_key('failure'):
            update.append("failure:'%s'" % options['update']['failure'])
        update = '{' + ','.join(update) + '}'
    elif options.get('update'):
        update += "'%s'" % options['update']
    
    function = "new Ajax.Request("
    if update: function = "new Ajax.Updater(%s, " % update
    
    function += "'%s'" % get_url(options['url'])
    function += ", %s)" % javascript_options
    
    if options.get('before'):
        function = "%s; %s" % (options['before'], function)
    if options.get('after'):
        function = "%s; %s" % (function, options['after'])
    if options.get('condition'):
        function = "if (%s) { %s; }" % (options['condition'], function)
    if options.get('confirm'):
        function = "if (confirm('%s')) { %s; }" % (escape_javascript(options['confirm']), function)
    
    return function

def observe_field(field_id, **options):
    """
    Observes the field with the DOM ID specified by ``field_id`` and makes
    an Ajax call when its contents have changed.
    
    Required keyword args are:
    
    ``url``
        ``url()``-style options for the action to call when the
        field has changed.
    
    Additional keyword args are:
    
    ``frequency``
        The frequency (in seconds) at which changes to this field will be
        detected. Not setting this option at all or to a value equal to or
        less than zero will use event based observation instead of time
        based observation.
    ``update``
        Specifies the DOM ID of the element whose innerHTML should be
        updated with the XMLHttpRequest response text.
    ``with_``
        A JavaScript expression specifying the parameters for the
        XMLHttpRequest. This defaults to 'value', which in the evaluated
        context refers to the new field value.
    
    Additionally, you may specify any of the options documented in
    `link_to_remote <#link_to_remote>`_.
    """
    if options.get('frequency') > 0:
        class_ = 'Form.Element.Observer'
    else:
        class_ = 'Form.Element.EventObserver'
    return build_observer(class_, field_id, **options)

def observe_form(form_id, **options):
    """
    Like `observe_field <#observe_field>`_, but operates on an entire form
    identified by the DOM ID ``form_id``.
    
    Keyword args are the same as observe_field, except the default value of
    the ``with_`` keyword evaluates to the serialized (request string) value
    of the form.
    """
    if options.get('frequency'):
        class_ = 'Form.Observer'
    else:
        class_ = 'Form.EventObserver'
    return build_observer(class_, form_id, submit=form_id, **options)

def options_for_ajax(options):
    js_options = build_callbacks(options)
    
    js_options['asynchronous'] = str(options.get('type') != 'synchronous').lower()
    if options.get('method'):
        if isinstance(options['method'], str) and options['method'].startswith("'"):
            js_options['method'] = options['method']
        else:
            js_options['method'] = "'%s'" % options['method']
    if options.get('position'):
        js_options['insertion'] = "Insertion.%s" % camelize(options['position'])
    js_options['evalScripts'] = str(options.get('script') is None or options['script']).lower()
    
    if options.get('form'):
        js_options['parameters'] = 'Form.serialize(this)'
    elif options.get('submit'):
        js_options['parameters'] = "Form.serialize('%s')" % options['submit']
    elif options.get('with_'):
        js_options['parameters'] = options['with_']
    
    return options_for_javascript(js_options)

def build_observer(cls, name, **options):
    if options.get('update') is True:
        options['with_'] = options.get('with', options.get('with_', 'value'))
    callback = remote_function(**options)
    javascript = "new %s('%s', " % (cls, name)
    if options.get('frequency'): 
        javascript += "%s, " % options['frequency']
    javascript += "function(element, value) {%s}" % callback
    if options.get('on'):
        # FIXME: our prototype isn't supporting the on arg
        javascript +=", '%s'" % options['on']
    javascript += ")"
    return javascript_tag(javascript)

def build_callbacks(options):
    callbacks = {}
    for callback, code in options.iteritems():
        if callback in CALLBACKS:
            name = 'on' + callback.title()
            callbacks[name] = "function(request){%s}" % code
    return callbacks

__all__ = ['link_to_remote', 'periodically_call_remote', 'form_remote_tag', 'submit_to_remote', 'update_element_function',
           'evaluate_remote_response', 'remote_function', 'observe_field', 'observe_form']
