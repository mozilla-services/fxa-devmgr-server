import binascii
import os


class Token:
    def __init__(self, data, algorithm, token_id, auth_key, **details):
        self.data = data
        self.algorithm = algorithm
        self.token_id = token_id
        self.auth_key = auth_key
        self.details = details

    def credentials(self):
        return dict(
            algorithm=self.algorithm,
            id=binascii.hexlify(self.token_id),
            key=binascii.hexlify(self.auth_key),
        )

    def to_hex(self):
        return binascii.hexlify(self.data)

    def update(self, **details):
        self.details.update(details)

    @classmethod
    def from_bytes(cls, key_manager, data):
        token_id, auth_key = key_manager.derive(cls.kind, data)
        return cls(data, key_manager.algorithm_name(), token_id, auth_key)

    @classmethod
    def from_hex(cls, key_manager, hex_data):
        data = binascii.unhexlify(hex_data)
        return cls.from_bytes(key_manager, data)

    @classmethod
    def create(cls, key_manager, **details):
        data = os.urandom(32)
        token_id, auth_key = key_manager.derive(cls.kind, data)
        return cls(data, key_manager.algorithm_name(),
                   token_id, auth_key, **details)


class SessionToken(Token):
    kind = 'sessionToken'

    @property
    def device_id(self):
        return self.details.get('device_id')

    @property
    def created_at(self):
        return self.details.get('created_at')

    def to_json(self):
        return dict(device_id=self.device_id.hex)
