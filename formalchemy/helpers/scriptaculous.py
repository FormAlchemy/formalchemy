"""
Scriptaculous Helpers

Provides a set of helpers for calling Scriptaculous JavaScript 
functions, including those which create Ajax controls and visual effects.

To be able to use these helpers, you must include the Prototype 
JavaScript framework and the Scriptaculous JavaScript library in your 
pages.

The Scriptaculous helpers' behavior can be tweaked with various options.
See the documentation at http://script.aculo.us for more information on
using these helpers in your application.
"""
# Last synced with Rails copy at Revision 6057 on Feb 9th, 2007.
import simplejson as json
from prototype import *
from javascript import options_for_javascript, array_or_string_for_javascript
from prototype import AJAX_OPTIONS, javascript_tag
from tags import camelize

def visual_effect(name, element_id=False, **js_options):
    """
    Returns a JavaScript snippet to be used on the Ajax callbacks for
    starting visual effects.
    
    Example::
    
        <% link_to_remote("Reload",  
                dict(url=url(action="reload"),
                     update="posts",
                     complete=visual_effect('highlight', "posts", duration=0.5))) %>
    
    If no element_id is given, it assumes "element" which should be a local
    variable in the generated JavaScript execution context. This can be 
    used for example with drop_receiving_element::
    
        <% drop_receving_element('some_element', loading=visual_effect('fade')) %>
    
    This would fade the element that was dropped on the drop receiving 
    element.
    
    For toggling visual effects, you can use ``toggle_appear``, ``toggle_slide``, and
    ``toggle_blind`` which will alternate between appear/fade, slidedown/slideup, and
    blinddown/blindup respectively.
    
    You can change the behaviour with various options, see
    http://script.aculo.us for more documentation.
    """
    element = (element_id and json.dumps(element_id)) or "element"
    if isinstance(js_options.get('queue'), dict):
        js_options['queue'] = '{%s}' % \
            ','.join(["%s:%s" % (k, (k == 'limit' and v) or "'%s'" % v) \
                          for k,v in js_options['queue'].iteritems()])
    elif js_options.has_key('queue'):
        js_options['queue'] = "'%s'" % js_options['queue']
    
    
    if 'toggle' in name:
        return "Effect.toggle(%s,'%s',%s);" % (element, name.replace('toggle_',''), options_for_javascript(js_options))
    return "new Effect.%s(%s,%s);" % (camelize(name), element, options_for_javascript(js_options))

def parallel_effects(*effects, **js_options):
    """
    Wraps visual effects so they occur in parallel
    
    Example::
    
        parallel_effects(
            visual_effect('highlight, 'dom_id'),
            visual_effect('fade', 'dom_id'),
        )
    """
    str_effects = [e[:e.rindex(';')] for e in effects] # Remove trailing ';'
    return "new Effect.Parallel([%s], %s)" % (','.join(str_effects), options_for_javascript(js_options))

def sortable_element(element_id, **options):
    """
    Makes the element with the DOM ID specified by ``element_id`` sortable.
    
    Uses drag-and-drop and makes an Ajax call whenever the sort order has
    changed. By default, the action called gets the serialized sortable
    element as parameters.
    
    Example::

        <% sortable_element("my_list", url=url(action="order")) %>
    
    In the example, the server-side action gets a "my_list" array
    parameter containing the values of the ids of elements the
    sortable consists of, in the current order (like
    ``mylist=item1&mylist=item2``, where ``item1`` and ``item2`` are
    the ids of the ``<li>`` elements).

    Note: For this to work, the sortable elements must have id
    attributes in the form ``string_identifier``. For example,
    ``item_1``. Only the identifier part of the id attribute will be
    serialized.
    
    You can change the behaviour with various options, see
    http://script.aculo.us for more documentation.
    """
    return javascript_tag(sortable_element_js(element_id, **options))

def sortable_element_js(element_id, **options):
    if not isinstance(element_id, basestring):
        raise ValueError('Argument element_id must be a string')
    options.setdefault('with_', "Sortable.serialize('%s')" % element_id)
    options.setdefault('onUpdate', "function(){%s}" % remote_function(**options))
    for k in options.keys():
        if k in AJAX_OPTIONS: del options[k]
    
    for option in ['tag', 'overlap', 'constraint', 'handle']:
        if options.has_key(option) and options[option]:
            options[option] = "'%s'" % options[option]
    
    if options.has_key('containment'):
        options['containment'] = array_or_string_for_javascript(options['containment'])
    if options.has_key('only'):
        options['only'] = array_or_string_for_javascript(options['only'])
    
    return "Sortable.create(%s, %s)" % (json.dumps(element_id), options_for_javascript(options))

def draggable_element(element_id, **options):
    """
    Makes the element with the DOM ID specified by ``element_id`` draggable.
    
    Example::

        <% draggable_element("my_image", revert=True)
    
    You can change the behaviour with various options, see
    http://script.aculo.us for more documentation.
    """
    return javascript_tag(draggable_element_js(element_id, **options))

def draggable_element_js(element_id, **options):
    return "new Draggable(%s, %s)" % (json.dumps(element_id), options_for_javascript(options))

def drop_receiving_element(element_id, **options):
    """
    Makes an element able to recieve dropped draggable elements
    
    Makes the element with the DOM ID specified by ``element_id`` receive
    dropped draggable elements (created by draggable_element) and make an
    AJAX call  By default, the action called gets the DOM ID of the element
    as parameter.
    
    Example::
    
        <% drop_receiving_element("my_cart", url=url_for(controller="cart", action="add" )) %>
    
    You can change the behaviour with various options, see
    http://script.aculo.us for more documentation.    
    """
    return javascript_tag(drop_receiving_element_js(element_id, **options))

def drop_receiving_element_js(element_id, **options):
    options.setdefault('with_', "'id=' + encodeURIComponent(element.id)")
    options.setdefault('onDrop', "function(element){%s}" % remote_function(**options))
    for k in options.keys():
        if k in AJAX_OPTIONS: del options[k]
    
    if options.has_key('accept'):
        options['accept'] = array_or_string_for_javascript(options['accept'])
    if options.has_key('hoverclass'):
        options['hoverclass'] = "'%s'" % options['hoverclass']
    
    return "Droppables.add(%s, %s)" % (json.dumps(element_id), options_for_javascript(options))

__all__ = ['visual_effect', 'parallel_effects', 'sortable_element', 'draggable_element', 'drop_receiving_element']
