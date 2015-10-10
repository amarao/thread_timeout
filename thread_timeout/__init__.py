#!/usr/bin/python
# (c) George Shuklin, 2015
#
# This library is free software; you can redistribute it and/or
# Modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# Version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# But WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from __future__ import print_function
import threading
import time
import sys
import ctypes
import wrapt  # pip install wrapt, apt-get install python-wrapt
from Queue import Queue
'''
    thread_timeout decorator allows to run piece of the python code
    safely regardless of TASK_UNINTERRUPTIBLE issues ('D' state).

    Main sources of 'D' state are broken NFS, bad disk/IO, or kernel bugs.

    Library provides single decorator, adding a timeout for the function call.


    Example of the usage:
        import thread_timeout

        @thread_timeout(10, kill=False)
        def NFS_read(path):
            file(path, 'r').read()

        try:
            print("Result: %s" % NFS_read('/broken_nfs/file'))
        except ExecTimeout:
            print ("NFS seems to be hung")


    thread_timeout works by running specified function in separate
    thread and waiting for timeout (or finalization) of the thread
    to return value or raise exception.
    If thread is not finished before timeout, thread_timeout will
    try to terminate thread according to kill value (see below).

    thread_timeout(timeout, kill=True, kill_wait=0.1)

    timeout - seconds, floating, how long to wait thread.
    kill - if True (default) attempt to terminate thread with function
    kill_wait - how long to wait after killing before reporting
    an unresponsive thread

    THREAD KILLING

    Thread killing implemented on python level: it will terminate python
    code, but will not terminate any IO operations or subprocess calls.

    Exceptions:

    ExecTimeout - function did not finish on time, timeout
        (base class for all following exceptions)
    KilledExecTimeout - there was a timeout and thread
        with function was killed successfully
    FailedKillExecTimeout - there was a timeout and kill attempt
        but the thread refuses to die
    NotKillExecTimeout - there was a timeout and there
        was no attempt to kill thread
'''


def _kill_thread(thread):
    # heavily based on http://stackoverflow.com/a/15274929/2281274
    # by Johan Dahlin
    # rewrited to avoid licence uncertainty

    # due to the strangeness in python 2.x, thread killing happens
    # within 32 python operations regardless of duration
    # (f.e. 32 x sleep(1), or 32 x sleep (0.01))
    # python3 works fine
    import sys
    SE = ctypes.py_object(SystemExit)
    tr = ctypes.c_long(thread.ident)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tr, SE)


class ExecTimeout(BaseException):
    pass


class KilledExecTimeout(ExecTimeout):
    pass


class FailedKillExecTimeout(ExecTimeout):
    pass


class NotKillExecTimeout(ExecTimeout):
    pass


def thread_timeout(delay, kill=True, kill_wait=0.04):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        queue = Queue()

        def inner_worker():
            try:
                result = wrapped(*args, **kwargs)
                queue.put(('success', result))
            except:
                e = sys.exc_info()
                queue.put(('exception', e))
        thread = threading.Thread(target=inner_worker)
        thread.daemon = True
        thread.start()
        thread.join(delay)
        if thread.isAlive():
            if not kill:
                raise NotKillExecTimeout(
                    "Timeout and no kill attempt")
            _kill_thread(thread)
            time.sleep(kill_wait)
            # FIXME isAlive is giving fals positive results
            if thread.isAlive():
                raise FailedKillExecTimeout(
                    "Timeout, thread refuses to die in %s seconds" %
                    kill_wait)
            else:
                raise KilledExecTimeout(
                    "Timeout and thread was killed")
        res = queue.get()
        if res[0] == 'success':
            return res[1]
        if res[0] == 'exception':
            raise res[1][0], res[1][1], res[1][2]
    return wrapper
