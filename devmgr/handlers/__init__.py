import tornado.web

from devmgr.handlers.base import ErrorHandler
from devmgr.handlers.device import (
    RegisterHandler,
    RegistrationHandler,
)
from devmgr.handlers.internal import (
    LoginHandler,
    RedirectionHandler,
)
from devmgr.handlers.user import (
    DeviceHandler,
    DevicesHandler,
)


def make_app(context):
    options = dict(
        default_handler_class=ErrorHandler,
        default_handler_args=dict(status=404, message='Resource not found'),
        context=context
    )
    return tornado.web.Application([
        (r'/v1/device/register', RegisterHandler),
        (r'/v1/device/registration', RegistrationHandler),

        (r'/v1/user/devices', DevicesHandler),
        (r'/v1/user/device/(.*)', DeviceHandler),

        (r'/internal/login', LoginHandler),
        (r'/internal/token', RedirectionHandler),
    ], **options)
