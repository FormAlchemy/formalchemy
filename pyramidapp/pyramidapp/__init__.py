from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramidapp.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'pyramidapp:static')
    config.add_route('home', '/', view='pyramidapp.views.my_view',
                     view_renderer='templates/mytemplate.pt')
    config.load_zcml('formalchemy:configure.zcml')
    config.add_route('fa_admin', '/admin/*traverse',
                     factory='formalchemy.ext.pyramid.admin.AdminView')
    config.registry.settings.update({
        'fa.models': config.maybe_dotted('pyramidapp.models'),
        'fa.forms': config.maybe_dotted('pyramidapp.forms'),
        'fa.session_factory': config.maybe_dotted('pyramidapp.models.DBSession'),
        })

    return config.make_wsgi_app()


