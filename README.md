Library to safely execute code without fear of the TASK\_UNINTERRUPTIBLE state
-----------------------------------------------------------------------------
thread\_timeout allows to run piece of the python code safely regardless 
of TASK\_UNINTERRUPTIBLE issues.

It provides single decorator, adding a timeout for the function call.


Example of the usage:

    import thread\_timeout

    @thread\_timeout(10, kill=False)
    def NFS\_read(path):
        file(path, 'r').read()

    try:
        print("Result: %s" % NFS\_read('/broken\_nfs/file'))
    except ExecTimeoutException:
        print ("NFS seems to be hung")


thread\_timeout works by running specified function in separate thread and waiting
for timeout (or finalization) of the thread to return value or raise Exception.
If thread is not finished before timeout, thread\_timeout may try to terminate
thread according to kill\_wait value (see below).

thread\_timeout(timeout, kill=True, kill\_wait=0.1)

timeout - seconds, floating, how long to wait thread.
kill - if True (default) attempt to terminate thread with function
kill\_wait - how long to wait after killing before reporting an unresponsive thread 

THREAD KILLING

Thread killing implemented on python level: it will terminate python code, but will not terminate any IO operations or subprocess calls.

Exceptions:

ExecTimeoutException - function did not finish on time, timeout (base class for all following exceptions)
KilledExecTimeoutException - there was a timeout and thread with function was killed successfully
FailedKillExecTimeoutException - there was a timeout and kill attempt but the thread refuses to die
NotKillExecTimeoutException - there was a timeout and there was no attempt to kill thread

