from devmgr.db import Device


class Registration(object):
    def __init__(self, request):
        self.request = request
        self.account_id = request.account_id
        self.db_session = self.request.registry.db_session

    def __getitem__(self, name):
        device = self.db_session.query(Device).get(name)
        if device:
            return device
        else:
            raise KeyError("No such device name found")

    def new_device(self, name, endpoint=None):
        device = Device(account_id=self.account_id, name=name,
                        endpoint=endpoint)
        self.db_session.add(device)
        self.db_session.commit()
        return device

    def all_devices(self):
        return self.db_session.query(Device).filter_by(
            account_id=self.account_id).all()


def make_root(request):
    return Registration(request)
