# -*- coding: utf-8 -*-

import sys
import types
from functools import wraps



if 'paper' not in sys.modules:
    paper = types.ModuleType('paper')
    paper.settings = __import__('settings')
    sys.modules['paper'] = paper
    sys.modules['paper.settings'] = paper.settings



from src.views import app


FUNCS = {}
def register(name):
    if name in FUNCS:
        raise Exception("register failure, name %s already registered" % name)
    
    def deco(func):
        FUNCS[name] = func
        @wraps(func)
        def wrap(*args, **kwargs):
            return func(*args, **kwargs)
        return wrap
    return deco

@register('run')
def _run():
    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('127.0.0.1', 8999), app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()
        
@register('syncdb')
def _syncdb():
    from src.models import sync
    sync()


if __name__ == '__main__':
    commands = FUNCS.keys()
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        usage = 'run as:\tpython {0} ' + ' | '.join(
            ['{%d}'%i for i in range(1, len(commands)+1)]
        )
        print usage.format(sys.argv[0], *commands)
        sys.exit(1)
        
    FUNCS[sys.argv[1]]()
