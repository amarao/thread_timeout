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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import threading
import time
import signal
import ctypes

'''
    thread_timeout allows to run piece of the python code safely regardless 
    of TASK_UNINTERRUPTIBLE issues.

    It provides single decorator, adding a timeout for the function call.


    Example of the usage:
        import thread_timeout

        @thread_timeout(10, kill=False)
        def NFS_read(path):
            file(path, 'r').read()

        try:
            print("Result: %s" % NFS_read('/broken_nfs/file'))
        except ExecTimeoutException:
            print ("NFS seems to be hung")


    thread_timeout works by running specified function in separate thread and waiting
    for timeout (or finalization) of the thread to return value or raise Exception.
    If thread is not finished before timeout, thread_timeout may try to terminate
    thread according to kill_wait value (see below).

    thread_timeout(timeout, kill=True, kill_wait=0.1)

    timeout - seconds, floating, how long to wait thread.
    kill - if True (default) attempt to terminate thread with function
    kill_wait - how long to wait after killing before reporting an unresponsive thread 
    
    THREAD KILLING

    Thread killing implemented on python level: it will terminate python code, but will not terminate any IO operations or subprocess calls.

    Exceptions:

    ExecTimeoutException - function did not finish on time, timeout (base class for all following exceptions)
    KilledExecTimeoutException - there was a timeout and thread with function was killed successfully
    FailedKillExecTimeoutException - there was a timeout and kill attempt but the thread refuses to die
    NotKillExecTimeoutException - there was a timeout and there was no attempt to kill thread
'''





def _kill_thread(t):
    # heavily based on http://stackoverflow.com/a/15274929/2281274
    # by Johan Dahlin
    # rewrited to avoid licence uncertainty
    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(t.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    else:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(t.ident, None)

class ExecTimeoutException(BaseException):
    pass

class KilledExecTimeoutException(ExecTimeoutException):
    pass

class FailedKillExecTimeoutException(ExecTimeoutException):
    pass

class NotKillExecTimeoutException(ExecTimeoutException):
    pass


def thread_timeout(delay, kill=True, kill_wait=0.1):
    def generate_decorator(function):
        def decorator (*args, **kwargs):
            result = [None]
            def inner_worker():
                result[0] = function(*args, **kwargs)
            thread = threading.Thread(target=inner_worker)
            thread.daemon = True
            thread.start()
            thread.join(delay)
            if thread.isAlive():
                    if not kill:
                        raise NotKillExecTimeoutException("Timeout and no kill attempt")
                    _kill_thread(thread)
                    time.sleep(kill_wait)
                    if thread.isAlive():
                        raise FailedKillExecTimeoutException("Timeout, thread refuses to die in %s seconds" % kill_wait)
                    else:
                        raise KilledExecTimeoutException("Timeout and thread was killed")
            return result[0]
        return decorator
    return generate_decorator

if __name__ == "__main__":
    print ("Running tests")
    @thread_timeout(2)
    def test1(delay):
        print ("  .. sleeing for %s" % delay)
        time.sleep(delay)
        print ("  .. done sleep for %s" % delay)
    try:
        res = test1(1)
        print ("Test1 OK")
    except ExecTimeoutException:
        print ("Test1 failed, timeout too soon")
    

    @thread_timeout(1)
    def test2(delay):
        print ("  .. sleeing for %s" % delay)
        time.sleep(delay)
        print("  .. done sleep for %s" % delay)

    try:
        test2(3)
        raise Exception("Test2 failed: timeout does not work")
    except ExecTimeoutException as e:
        print ("  .. got excepted execption %s"%repr(e))
        print("Test2 OK")

    @thread_timeout(1)
    def test3(x):
        return x

    if test3('OK') != 'OK':
        print ("Test3 failed, %s", repr(test3('OK')))
    else:
        print ("Test3 OK")

    @thread_timeout(1)
    def test4(x):
        for a in range(0,x):
            time.sleep(2)
    try:
        test4(2)
    except FailedKillExecTimeoutException as e:
        print ("Test4 OK, got expected exception %s" % repr(e))

    @thread_timeout(1, kill=False)
    def test5(x):
        for a in range(0,x):
            time.sleep(2)
    try:
        test5(2)
    except NotKillExecTimeoutException as e:
        print ("Test5 OK, got expected exception %s" % repr(e))
    
