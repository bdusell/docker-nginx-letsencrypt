# watchdog.py
# An supervisord event listener which stops supervisord whenever any process
# exits, so that an external process manager can detect that the container has
# a problem.
#
# NOTE: Assumes Python 2.
#
# Partly based on:
# https://github.com/Supervisor/superlance/blob/master/superlance/crashmail.py
# and
# https://github.com/Supervisor/supervisor/issues/712

import os
import signal
import sys
import traceback
import xmlrpclib

import supervisor.childutils
import supervisor.xmlrpc

def log(msg):
    sys.stderr.write('watchdog.py: ')
    sys.stderr.write(msg)
    sys.stderr.write('\n')
    sys.stderr.flush()

def kill_supervisord():
    os.kill(get_supervisord_pid(), signal.SIGTERM)

def get_supervisord_pid():
    with open('/tmp/supervisord.pid') as fin:
        pid_str = fin.read()
    return int(pid_str)

# See https://github.com/Supervisor/supervisor/blob/3.3.5/supervisor/childutils.py#L52-L56
def wait_after_ready():
    line = sys.stdin.readline()
    headers = supervisor.childutils.get_headers(line)
    payload = sys.stdin.read(int(headers['len']))
    return headers, payload

def main():
    # Tell supervisord that we are ready to receive events. If this is not
    # done right away, then there is a race condition where a service can fail
    # after we check that all processes are running and before we start
    # listening for events. Events should be buffered on stdin if we are busy
    # checking processes.
    supervisor.childutils.listener.ready()
    # Because a process can fail before the event listener is started, we need
    # to verify that all processes are running using Supervisor's XML-RPC API.
    # A process could fail immediately if, for example, the Nginx configuration
    # file has a syntax error.
    # See http://supervisord.org/xmlrpc.html
    # and http://supervisord.org/api.html
    # and https://stackoverflow.com/questions/11743378/talking-to-supervisord-over-xmlrpc
    log('connecting to supervisord via XML-RPC API')
    server = xmlrpclib.ServerProxy('http://127.0.0.1',
        transport=supervisor.xmlrpc.SupervisorTransport(
            None,
            None,
            'unix:///tmp/supervisord.sock'))
    processes = server.supervisor.getAllProcessInfo()
    log('checking running processes')
    for process in processes:
        if process['group'] != 'watchdog':
            if process['statename'] not in ('STARTING', 'RUNNING'):
                log('process %(group)s is in %(statename)s state; shutting down' % process)
                kill_supervisord()
                return
    log('all processes are running; listening for events')
    # Listen for events. Kill supervisord whenever any process exits.
    # wait_after_ready() is just like wait() except that it does not call
    # ready() at the beginning. Since we already called ready() once, it would
    # be an error to call it again.
    headers, payload = wait_after_ready()
    while True:
        eventname = headers.get('eventname')
        if eventname == 'PROCESS_STATE_EXITED':
            pheaders, pdata = supervisor.childutils.eventdata(payload + '\n')
            log('process %(processname)s exited; stopping supervisord...' % pheaders)
            kill_supervisord()
        else:
            log('ignoring event of type %s' % eventname)
        supervisor.childutils.listener.ok(sys.stdout)
        headers, payload = supervisor.childutils.listener.wait(
            sys.stdin, sys.stdout)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # If an unexpected error happens, make sure to kill supervisor on the
        # way out.
        log(str(e))
        traceback.print_exc(file=sys.stderr)
        kill_supervisord()
