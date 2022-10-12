import os


def numCPUs():
    if not hasattr(os, "sysconf"):
        raise RuntimeError("No sysconf detected.")
    return os.sysconf("SC_NPROCESSORS_ONLN")


bind = "127.0.0.1:2009"
workers = 4
backlog = 2048
worker_class = "gevent"
debug = True
daemon = False
pidfile = "/tmp/veggies_service-gunicorn.pid"
logfile = "/tmp/veggies_service-gunicorn.log"
loglevel = 'info'
accesslog = '/tmp/gunicorn-access-veggies_service.log'