import uuid

from devmgr.errors import ProtocolError
from devmgr.models.device import Device
from devmgr.handlers.base import (BaseHandler, HawkHandler)
from tornado import gen
from tornado.escape import json_decode


class RegisterHandler(BaseHandler):
    '''Registers a device with the device manager.

    This endpoint exchanges an FxA assertion for an OAuth token,
    fetches the authenticating user's account ID, creates a device
    record, and issues a session token. It is called by the Gecko
    client when the user creates or logs into a Firefox Account.
    '''
    access_token = None
    user_id = None
    email = None

    @gen.coroutine
    def post(self):
        body = None
        try:
            body = json_decode(self.request.body)
        except:
            pass

        assertion = None
        if isinstance(body, dict):
            assertion = body.get('assertion')
        if not assertion:
            raise ProtocolError(999, 400, 'Invalid FxA assertion')

        yield self.decode_assertion(assertion)
        if not self.has_credentials():
            raise ProtocolError(999, 403, 'Missing or invalid credentials')

        device_id = uuid.uuid4()
        device = Device(self.user_id, device_id, email=self.email)
        yield self.context.devices.put(device)

        yield self.create_session(device_id)

        response = device.to_json()
        # TODO: The exchanged token is included in the body for testing. This
        # should never be enabled in production.
        response['insecure_access_token_for_testing'] = self.access_token
        self.write_json(response)

    def has_credentials(self):
        return self.user_id is not None and self.email is not None

    @gen.coroutine
    def decode_assertion(self, assertion):
        code = yield self.context.executor.submit(
            self.context.fxa_oauth.authorize_code,
            assertion,
            scope='profile'
        )
        if not code:
            raise ProtocolError(999, 400, 'Missing authorization code')

        self.access_token = yield self.context.executor.submit(
            self.context.fxa_oauth.trade_code,
            code
        )
        if not self.access_token:
            raise ProtocolError(999, 400, 'Invalid access token')

        profile = yield self.context.executor.submit(
            self.context.fxa_profile.get_profile,
            self.access_token
        )
        self.user_id = profile.get('uid')
        self.email = profile.get('email')


class RegistrationHandler(HawkHandler):
    '''Updates or deletes a device record.'''

    @gen.coroutine
    def get(self):
        # Get device name, push endpoint, other metadata.
        raise ProtocolError(999, 500, 'Not yet implemented')

    @gen.coroutine
    def patch(self):
        # Update metadata.
        raise ProtocolError(999, 500, 'Not yet implemented')

    @gen.coroutine
    def delete(self):
        # Destroy the device record. Called by the client on logout.
        raise ProtocolError(999, 500, 'Not yet implemented')
