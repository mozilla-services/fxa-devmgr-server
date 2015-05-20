import devmgr.handlers
import tornado.ioloop

from devmgr import log
from devmgr.context import Context


def main(sysargs=None):
    loop = tornado.ioloop.IOLoop.instance()
    context = Context(loop)

    app = devmgr.handlers.make_app(context)
    app.listen(8787)
    try:
        loop.start()
    except KeyboardInterrupt:
        log.debug('Bye')

if __name__ == '__main__':
    main()
