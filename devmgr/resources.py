from pyramid.security import Allow, Authenticated

from devmgr.db import Device


class Registration(object):
    __acl__ = [
        (Allow, Authenticated, "create")
    ]

    def __init__(self, request):
        self.request = request
        self.db_session = self.request.registry.db_session
        self.__acl__.append(
            (Allow, "account_id:%s" % request.credentials.account_id, "get")
        )

    def __getitem__(self, name):
        device = self.db_session.query(Device).get(name)
        if device:
            device.__acl__ = [
                (Allow, "account_id:%s" % device.uuid, "update"),
                (Allow, "recent_account_id:%s" % device.uuid, "delete")
            ]
            return device
        else:
            raise KeyError("No such device name found")

    def new_device(self, account_id, name, endpoint=None):
        device = Device(account_id=account_id, name=name, endpoint=endpoint)
        self.db_session.add(device)
        self.db_session.commit()
        return device

    def all_devices(self):
        return self.db_session.query(Device).filter_by(
            account_id=self.request.credentials.account_id).all()


def make_root(request):
    return Registration(request)
