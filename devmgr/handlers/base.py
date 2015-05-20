import binascii
import mohawk
import sys
import time
import tornado.web

from devmgr import log
from devmgr.errors import ProtocolError
from devmgr.models.token import SessionToken
from fxa.errors import InProtocolError
from mohawk.exc import (HawkFail, TokenExpired)
from mohawk.util import parse_authorization_header
from tornado import gen
from tornado.escape import (json_encode, utf8)


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, app, request, **kwargs):
        super(BaseHandler, self).__init__(app, request, **kwargs)
        self.context = app.settings['context']

    def set_default_headers(self):
        self.clear_header('Server')
        self.set_header('Timestamp', int(time.time()))
        self.add_header('Access-Control-Expose-Headers', 'Timestamp')
        self.add_header('Access-Control-Expose-Headers', 'Hawk-Session-Token')

    @gen.coroutine
    def get_session(self):
        header = self.request.headers.get('Authorization')
        if not header:
            self.set_header('WWW-Authenticate', 'Hawk')
            raise ProtocolError(999, 401, 'Missing authorization header')

        attributes = None
        try:
            attributes = parse_authorization_header(header)
        except HawkFail:
            self.set_header('WWW-Authenticate', 'Hawk')
            raise ProtocolError(999, 401, 'Invalid authorization header')

        token_id_hex = attributes.get('id')
        if not token_id_hex:
            raise ProtocolError(999, 401, 'Missing session token ID')

        token_id = binascii.unhexlify(token_id_hex)
        token = yield self.context.sessions.get(token_id)
        if not token:
            raise ProtocolError(999, 403, 'Invalid session token')
        self.current_user = token

    @gen.coroutine
    def create_session(self, device_id):
        token = yield self.context.executor.submit(
            SessionToken.create,
            self.context.key_manager,
            device_id=device_id,
            created_at=int(time.time()),
        )
        yield self.context.sessions.put(token)
        self.current_user = token
        self.set_header('Hawk-Session-Token', self.current_user.to_hex())

    def authenticate_payload(self, content_type, chunk):
        pass

    def write_json(self, data):
        content_type = 'application/json; charset=UTF-8'
        chunk = utf8(json_encode(data))

        self.set_header('Content-Type', content_type)
        self.authenticate_payload(content_type, chunk)
        self.write(chunk)

    def write_error(self, status_code, **kwargs):
        cls, value, traceback = kwargs.get('exc_info')
        response = value if issubclass(cls, ProtocolError) else ProtocolError(
            code=status_code,
        )
        self.finish(response.payload())


class HawkHandler(BaseHandler):
    '''A base class that authenticates clients using a Hawk session token.'''
    def seen_nonce(self, nonce, timestamp):
        # Log client clock skew values. No need to maintain a nonce cache,
        # since timestamp checks are disabled.
        log.debug('skew: %d', time.time() - float(timestamp))

    def set_default_headers(self):
        self.add_header('Access-Control-Expose-Headers', 'WWW-Authenticate')
        self.add_header('Access-Control-Expose-Headers',
                        'Server-Authorization')
        super(HawkHandler, self).set_default_headers()

    def authenticate_payload(self, content_type, chunk):
        if self._receiver:
            auth = yield self.context.executor.submit(
                self._receiver.respond,
                content=chunk,
                content_type=content_type,
            )
            self.set_header('Server-Authorization', auth)

    def get_credentials(self, token_id):
        return self.current_user.credentials()

    @gen.coroutine
    def prepare(self):
        yield self.get_session()
        try:
            self._receiver = mohawk.Receiver(
                credentials_map=self.get_credentials,
                # TODO: `Receiver` should accept a pre-parsed header.
                request_header=self.request.headers.get('Authorization'),
                url=self.request.full_url(),
                method=self.request.method,
                content=self.request.body,
                content_type=self.request.headers.get('Content-Type'),
                seen_nonce=self.seen_nonce,
                # The FxA auth server sees significant clock skew for client
                # requests. Bypass timestamp checking by setting the skew to
                # 20 years.
                timestamp_skew_in_seconds=20 * 365 * 24 * 60 * 60,
            )
        except TokenExpired as exc:
            log.warn('Token expired')
            self.set_header('WWW-Authenticate', exc.www_authenticate)
            raise ProtocolError(999, 401, 'Token expired')

        except HawkFail as exc:
            log.warn('Invalid credentials: %r', exc_info=sys.exc_info())
            raise ProtocolError(999, 403, 'Invalid credentials')


class OAuthHandler(BaseHandler):
    user_id = None

    @gen.coroutine
    def prepare(self):
        header = self.request.headers.get('Authorization')
        if not header:
            self.set_header('WWW-Authenticate', 'Bearer')
            raise ProtocolError(999, 401, 'Missing authorization')

        parts = header.split(' ', 1)
        if len(parts) < 2 or parts[0] != 'Bearer':
            self.set_header('WWW-Authenticate', 'Bearer')
            raise ProtocolError(999, 401, 'Invalid authorization')

        try:
            response = yield self.context.executor.submit(
                self.context.fxa_oauth.verify_token,
                token=parts[1],
                scope='profile'
            )
        except InProtocolError as err:
            log.warn('Invalid bearer token: %r', err)
            raise ProtocolError(999, 403, 'Invalid bearer token')
        except:
            raise ProtocolError(999, 503, 'OAuth server unavailable')

        self.user_id = response.get('user')


class ErrorHandler(BaseHandler):
    def initialize(self, status, message=None):
        self.status = status
        self.message = message

    def prepare(self):
        raise ProtocolError(999, self.status, self.message)
