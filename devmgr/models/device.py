class Device:
    def __init__(self, user_id, device_id, **details):
        self.user_id = user_id
        self.device_id = device_id
        self.details = details

    @property
    def name(self):
        return self.details.get('name')

    @property
    def kind(self):
        return self.details.get('kind')

    @property
    def session_id(self):
        return self.details.get('session_id')

    @property
    def push_endpoint(self):
        return self.details.get('push_endpoint')

    def update(self, **details):
        self.details.update(details)

    def to_json(self):
        result = dict(device_id=self.device_id.hex)
        name = self.name
        if name:
            result['name'] = name

        kind = self.kind
        if kind:
            result['kind'] = kind

        push_endpoint = self.push_endpoint
        if push_endpoint:
            result['push_endpoint'] = push_endpoint

        return result
