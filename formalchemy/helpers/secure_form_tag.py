"""
Secure Form Tag Helpers -- For prevention of Cross-site request forgery (CSRF)
attacks.

Generates form tags that include client-specific authorization tokens to be
verified by the destined web app.

Authorization tokens are stored in the client's session. The web app can then
verify the request's submitted authorization token with the value in the
client's session.

This ensures the request came from the originating page. See
http://en.wikipedia.org/wiki/Cross-site_request_forgery for more information.

Pylons provides an ``authenticate_form`` decorator that does this verfication
on the behalf of controllers.
"""
import random

from routes import request_config

from form_tag import form, hidden_field
from prototype import form_remote_tag
from tags import content_tag

token_key = '_authentication_token'

def get_session():
    """Return the current session from the environ provided by routes. A Pylons
    supported session is assumed. A KeyError is raised if one doesn't exist."""
    environ = request_config().environ
    session_key = environ['pylons.environ_config']['session']
    session = environ[session_key]
    return session

def authentication_token():
    """Return the current authentication token, creating one if one doesn't
    already exist."""
    session = get_session()
    if not token_key in session:
        try:
            token = str(random.getrandbits(128))
        except AttributeError: # Python < 2.4
            token = str(random.randrange(2**128))
        session[token_key] = token
        if hasattr(session, 'save'):
            session.save()
    return session[token_key]

def secure_form(url, **args):
    """Create a form tag (like webhelpers.rails.form_tag.form) including a
    hidden authentication token field.
    """
    id = authentication_token()
    form_html = form(url, **args)
    return '%s\n%s' % (form_html,
                       content_tag('div', hidden_field(token_key, id),
                                   style='display: none;'))

def secure_form_remote_tag(**args):
    """Create a form tag (like webhelpers.rails.prototype.form_remote_tag)
    including a hidden authentication token field.
    """
    id = authentication_token()
    form_html = form_remote_tag(**args)
    return '%s\n%s' % (form_html,
                       content_tag('div', hidden_field(token_key, id),
                                   style='display: none;'))

__all__ = ['secure_form', 'secure_form_remote_tag']
