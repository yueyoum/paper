import os

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
RUN_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '../run'))

daemon = True
bind = "127.0.0.1:8999"
backlog = 1024
workers = 2
worker_class = "gevent_pywsgi"
max_requests = 1000

pidfile = os.path.join(RUN_PATH, 'gunicorn.pid')
accesslog = os.path.join(RUN_PATH, 'gunicorn_access.log')
errorlog = os.path.join(RUN_PATH, 'gunicorn_error.log')
