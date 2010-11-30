from pyramid.configuration import Configurator
from pyramid.settings import asbool

#from pyramid_beaker import session_factory_from_settings

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    from pyramidapp.models import initialize_sql
    db_string = settings.get('db_string')
    if db_string is None:
        raise ValueError("No 'db_string' value in application "
                         "configuration.")
    initialize_sql(db_string, asbool(settings.get('db_echo')))
    config = Configurator(settings=settings)
    config.begin()
    #session_factory = session_factory_from_settings(settings)
    #config.set_session_factory(session_factory)
    config.add_static_view('static', 'pyramidapp:static/')
    config.add_handler('main', '/:action', 'pyramidapp.handlers:MyHandler')
    config.add_handler('home', '/', 'pyramidapp.handlers:MyHandler',
                       action='index')
    config.add_subscriber('pyramidapp.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    config.load_zcml('formalchemy:configure.zcml')
    config.add_route('fa_admin', '/admin/*traverse',
                     factory='formalchemy.ext.pyramid.admin.AdminView')
    config.registry.settings.update({
        'fa.models': config.maybe_dotted('pyramidapp.models'),
        'fa.session_factory': config.maybe_dotted('pyramidapp.models.DBSession'),
        })

    config.end()
    return config.make_wsgi_app()
