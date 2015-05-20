from devmgr.errors import ProtocolError
from devmgr.handlers.base import OAuthHandler
from tornado import gen


class DeviceHandler(OAuthHandler):
    @gen.coroutine
    def get(self, device_id):
        '''Returns device metadata to a relying service.'''
        device = yield self.context.devices.get(
            self.user_id,
            device_id,
        )
        if not device:
            raise ProtocolError(999, 500, 'Nonexistent device ID')
        self.write_json(device.to_json())

    @gen.coroutine
    def put(self, device_id):
        # TODO: Update device name from a Backbone view served by the
        # content server.
        raise ProtocolError(999, 500, 'Not yet implemented')

    @gen.coroutine
    def delete(self, device_id):
        # Remote logout.
        raise ProtocolError(999, 500, 'Not yet implemented')


class DevicesHandler(OAuthHandler):
    @gen.coroutine
    def get(self):
        '''Lists all devices associated with a user's account.'''
        devices = yield self.context.devices.get_all(self.user_id)
        response = [device.to_json() for device in devices]
        self.write_json(response)
