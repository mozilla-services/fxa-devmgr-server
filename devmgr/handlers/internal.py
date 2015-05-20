from devmgr.errors import ProtocolError
from devmgr.handlers.base import BaseHandler
from tornado import gen


class LoginHandler(BaseHandler):
    def get(self):
        '''A test-only handler that initiates the OAuth redirection flow.

        The device manager will not obtain OAuth tokens directly;
        instead, relying services will authenticate the user and
        provide the bearer token to the device endpoints.'''
        redirect_url = self.context.fxa_oauth.get_redirect_url(
            state='under-no-circumstances-should-this-be-enabled-in-prod',
            scope='profile',
        )
        self.redirect(redirect_url)


class RedirectionHandler(BaseHandler):
    access_token = None

    @gen.coroutine
    def get(self):
        code = self.get_query_argument('code', default=None)
        if not code:
            raise ProtocolError(999, 400, 'Missing OAuth code')

        self.access_token = yield self.context.executor.submit(
            self.context.fxa_oauth.trade_code,
            code,
        )
        self.write_json(dict(
            access_token=self.access_token,
        ))
