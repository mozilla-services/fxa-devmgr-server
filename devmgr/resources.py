from sqlalchemy.orm import joinedload
from pyramid.security import Allow, Authenticated

from devmgr.db import Device


class Registration(object):
    __acl__ = [
        (Allow, Authenticated, "create")
    ]

    def __init__(self, request):
        self.request = request
        if request.credentials:
            self.__acl__.append(
                (Allow, "account_id:%s" % request.credentials.account_id, "get")
            )

    def __getitem__(self, name):
        device = self.request.db.query(Device).options(
            joinedload(Device.tokens)).get(name)
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
        self.request.db.add(device)
        self.request.db.commit()
        return device

    def all_devices(self):
        return self.request.db.query(Device).filter_by(
            account_id=self.request.credentials.account_id).all()


def make_root(request):
    return Registration(request)
