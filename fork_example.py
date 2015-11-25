import thread_timeout
import os
import time

print "mypid", os.getpid()
thread_timeout.continue_in_fork()
print "mypid", os.getpid()
print "Press Ctrl-C"
time.sleep(15)
