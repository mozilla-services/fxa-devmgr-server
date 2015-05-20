import uuid

from devmgr.models.device import Device
from devmgr.models.token import SessionToken
from tornado import gen


class SessionStore:
    def __init__(self, key_manager):
        self.sessions = {}
        self.key_manager = key_manager

    @gen.coroutine
    def get(self, token_id):
        record = self.sessions.get(token_id)
        if not record:
            return None
        token = SessionToken.from_hex(self.key_manager, record['data'])
        token.update(
            device_id=uuid.UUID(hex=record['device_id']),
            created_at=record['created_at']
        )
        return token

    @gen.coroutine
    def put(self, token):
        record = dict(
            data=token.to_hex(),
            device_id=token.device_id.hex,
            created_at=token.created_at,
        )
        self.sessions[token.token_id] = record

    @gen.coroutine
    def delete(self, token_id):
        del self.sessions[token_id]


class DeviceStore:
    def __init__(self):
        self.devices = {}

    @gen.coroutine
    def get_all(self, user_id):
        '''Returns a list of the user's devices.'''
        matches = [self.devices[(x, device_id)]
                   for x, device_id in self.devices if x == user_id]
        return map(self._to_device, matches)

    @gen.coroutine
    def get(self, user_id, device_id):
        key = (user_id, device_id)
        record = self.devices.get(key)
        return self._to_device(record) if record else None

    @gen.coroutine
    def put(self, device):
        key = (device.user_id, device.device_id.hex)
        self.devices[key] = dict(
            user_id=device.user_id,
            device_id=device.device_id.hex,
            name=device.name,
            kind=device.kind,
            session_id=device.session_id,
            push_endpoint=device.push_endpoint,
        )

    @gen.coroutine
    def delete(self, device):
        key = (device.user_id, device.device_id.hex)
        del self.devices[key]

    def _to_device(self, record):
        return Device(
            user_id=record['user_id'],
            device_id=uuid.UUID(hex=record['device_id']),
            name=record['name'],
            kind=record['kind'],
            session_id=record['session_id'],
            push_endpoint=record['push_endpoint'],
        )
