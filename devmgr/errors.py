import tornado.web


class ProtocolError(tornado.web.HTTPError):
    errno = None

    def __init__(self, errno=999, code=500, message='Unspecified error',
                 *args, **kwargs):
        super(ProtocolError, self).__init__(code, log_message=message,
                                            *args, **kwargs)
        self.errno = errno

    def payload(self):
        return dict(
            code=self.status_code,
            errno=self.errno,
            message=self.log_message
        )
