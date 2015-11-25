#!/usr/bin/python

from thread_timeout import *
import time
from nose import run

def test1():
    ''' timeout is not stopping quick function
    '''
    @thread_timeout(2)
    def func(delay):
        time.sleep(delay)

    func(1)


def test2():
    ''' ExecTimeout
    '''
    @thread_timeout(1)
    def func(delay):
        time.sleep(delay)

    try:
        func(3)
        raise Exception("Test2 failed: timeout does not work")
    except ExecTimeout as e:
        pass


def test3():
    ''' function returns result
    '''
    @thread_timeout(1)
    def func(x):
        return x

    assert func('OK') == 'OK'


def test4():
    ''' FailedKillExecTimeout
    '''
    @thread_timeout(1)
    def looong():
        time.sleep(3)
    try:
        looong()
        raise Exception('FailedKillExecTimeout was expected')
    except FailedKillExecTimeout:
        pass


def test5():
    ''' NotKillExecTimeout
    '''
    @thread_timeout(1, kill=False)
    def looong_and_unkillable():
            time.sleep(2)
    try:
        looong_and_unkillable()
        raise Exception('NotKillExecTimeout was expected')
    except NotKillExecTimeout as e:
        print("Test5 OK, got expected exception %s" % repr(e))


def test6():
    '''KilledExecTimeout
    '''
    @thread_timeout(1, kill_wait=0.40)
    def killme():
        for a in range(0, 200):
            time.sleep(0.01)
        raise Exception("Not killed!")

    try:
        killme()
    except KilledExecTimeout:
        pass


def test7():
    ''' decorator is not changing python's into inspection
    '''
    from inspect import getargspec

    def func(x, y=1, *args, **kwargs):
        return vars()

    func_with_timeout = thread_timeout(1)(func)
    assert getargspec(func) == getargspec(func_with_timeout)


def test8():
    ''' Class methods
    '''
    class Class(object):

        @thread_timeout(1)
        def short(self, x):
            return x

        @thread_timeout(1, kill_wait=0.33)
        def looong(self, x):
            for x in range(0, 300):
                time.sleep(0.01)
            return x

    obj = Class()
    res = obj.short("OK")
    assert res == 'OK'
    try:
        res = obj.looong('KO')
    except KilledExecTimeout:
        pass


def test9():
    '''Check if exceptions are carried properly
    '''
    @thread_timeout(1, kill=False)
    def exception(e):
        raise e

    exception_list = (
                    OverflowError,
                    ReferenceError,
                    SyntaxError,
                    ZeroDivisionError,
                    FloatingPointError,
                    BufferError,
                    LookupError,
                    AssertionError,
                    AttributeError,
                    TypeError,
                    EOFError,
                    IOError,
                    ImportError,
                    IndexError,
                    KeyError,
                    KeyboardInterrupt,
                    MemoryError,
                    NameError,
                    NotImplementedError,
                    OSError,
                    UnboundLocalError,
                    UnicodeError,
                    ValueError,
                    ExecTimeout
                    )
    for exc in exception_list:
        try:
            exception(exc)
        except exc as e:
            pass


def test10():
    '''Check if decorator stacking works (inner first)
    '''
    @thread_timeout(2)
    def outer():
        @thread_timeout(1)
        def inner():
            for x in range(0, 500):
                time.sleep(0.01)
        inner()

    begin = time.time()
    try:
        outer()
    except ExecTimeout as e:
        pass
    assert 1 < time.time() - begin < 2


def test11():
    '''Check if decorator stacking works (outer first)
    '''
    @thread_timeout(1)
    def outer():
        @thread_timeout(2)
        def inner():
            for x in range(0, 500):
                time.sleep(0.01)
        inner()

    begin = time.time()
    try:
        outer()
    except ExecTimeout:
        pass
    assert 1 < time.time() - begin < 2


def test12():
    '''Check if decorator waits before kill'''
    @thread_timeout(3)
    def outer():
        @thread_timeout(3)
        def inner():
            for x in range(0, 100):
                time.sleep(0.01)
        inner()

    begin = time.time()
    outer()
    assert 1 < time.time() - begin < 3

def test13():
    '''check if we can instance methods with one kwarg (real bug case)'''
    class Foo:
        @thread_timeout(1)
        def bar(self, arg=1):
            pass

    foo = Foo()
    foo.bar(arg=0)

if __name__ == "__main__":
    print("Running tests")

    run(argv=[
        '', __file__,
        '-v'
    ])
