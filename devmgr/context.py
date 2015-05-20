import fxa.oauth
import fxa.profile

from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from devmgr.db.memory import (DeviceStore, SessionStore)


class KeyManager:
    def __init__(self, prefix):
        self.prefix = prefix
        self._algorithm = hashes.SHA256
        self._backend = default_backend()

    def algorithm_name(self):
        return self._algorithm.name

    def derive(self, kind, data):
        hkdf = HKDF(
            algorithm=self._algorithm(),
            length=2*32,
            salt=b'',
            info=(self.prefix + kind).encode('ascii'),
            backend=self._backend
        )
        key_material = hkdf.derive(data)
        token_id = key_material[0:32]
        auth_key = key_material[32:64]
        return (token_id, auth_key)


class Context:
    client_id = '94f9b10107c39576'
    client_secret = ('ff7d067b311b393e1cd290e906004e927097772c96d54268875aec92'
                     '25c51133')

    profile_server_url = 'http://127.0.0.1:1111'
    oauth_server_url = 'http://127.0.0.1:9010'

    def __init__(self, loop):
        self.loop = loop
        self.executor = ThreadPoolExecutor(4)
        self.key_manager = KeyManager('identity.mozilla.com/picl/v1/')

        self.sessions = SessionStore(self.key_manager)
        self.devices = DeviceStore()

        self.fxa_oauth = fxa.oauth.Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_url=self.oauth_server_url,
        )
        self.fxa_profile = fxa.profile.Client(
            server_url=self.profile_server_url,
        )
