import pyramid.renderers
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import NewRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from devmgr.db import Base
from devmgr.resources import make_root
from devmgr.security import DevMgrAuthenticationPolicy


class Creds(object):
    pass


def verify_auth(event):
    req = event.request
    cred = Creds()
    cred.account_id = "fred"
    cred.recent = False
    req.credentials = cred


def db(request):
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()
    request.add_finished_callback(cleanup)
    return session


def make_app(global_config, db_uri="sqlite:////tmp/devmgr.db", **settings):
    # Security policies
    authentication_policy = DevMgrAuthenticationPolicy()
    authorization_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory=make_root,
        authentication_policy=authentication_policy,
        authorization_policy=authorization_policy,
    )
    config.add_subscriber(verify_auth, NewRequest)
    config.add_request_method(db, reify=True)

    db_engine = create_engine(db_uri)
    session_factory = sessionmaker(bind=db_engine)
    config.registry.dbmaker = scoped_session(session_factory)
    Base.metadata.create_all(db_engine)

    json_renderer = pyramid.renderers.JSON()
    config.add_renderer(None, json_renderer)
    config.include('devmgr.views.include_views')
    return config.make_wsgi_app()
