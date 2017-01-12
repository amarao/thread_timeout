Library to safely execute code without fear of the TASK\_UNINTERRUPTIBLE state
-----------------------------------------------------------------------------
thread\_timeout allows to run given piece of python code safely regardless 
of TASK\_UNINTERRUPTIBLE issues.

It provides a single decorator with a timeout for a function call.

Example:

    import thread_timeout

    @thread_timeout(10, kill=False)
    def NFS_read(path):
        file(path, 'r').read()

    try:
        print("Result: %s" % NFS_read('broken_nfs/file'))
    except ExecTimeoutException:
        print ("NFS seems to be hung")


thread\_timeout works by running specified function in a separate thread and waiting
for timeout (or termination) of the thread. It returns to functions return value
or reraise exception.

If thread does not finish before timeout, thread\_timeout may try to terminate
thread according to kill\_wait value (see below).

thread\_timeout(timeout, kill=True, kill\_wait=0.1)

timeout - seconds, floating, how long to wait thread.
kill - if True (default) attempt to terminate thread with function
kill\_wait - how long to wait after killing before reporting an unresponsive thread 

THREAD KILLING

Thread killing implemented on python level: it will terminate python code, but will not terminate
any IO operations or subprocess calls.

Exceptions:

ExecTimeoutException - function did not finish on time, timeout (base class for all following exceptions)
KilledExecTimeoutException - there was a timeout and thread with function was killed successfully
FailedKillExecTimeoutException - there was a timeout and kill attempt but the thread refuses to die
NotKillExecTimeoutException - there was a timeout and there was no attempt to kill thread

