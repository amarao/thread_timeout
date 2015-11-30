#!/usr/bin/python

import pytest
import time
from thread_timeout import *

def test_no_timeout():
    ''' timeout is not stopping quick function
    '''
    @thread_timeout(2)
    def func(delay):
        time.sleep(delay)

    func(0.5)


def test_raises():
    'ExecTimeout is raised'
    @thread_timeout(1)
    def func(delay):
        time.sleep(delay)

    with pytest.raises(ExecTimeout):
        func(3)

def test_function_return():
    'function returns result'
    @thread_timeout(1)
    def func(x):
        return x

    assert( func('OK') == 'OK')


def test_FailedKillExecTimeout():
    @thread_timeout(1)
    def looong():
        time.sleep(3)
    with pytest.raises(FailedKillExecTimeout):
        looong()


def test_NotKillExecTimeout():
    @thread_timeout(1, kill=False)
    def looong_and_unkillable():
            time.sleep(2)
    try:
        looong_and_unkillable()
        raise Exception('NotKillExecTimeout was expected')
    except NotKillExecTimeout as e:
        print("Test5 OK, got expected exception %s" % repr(e))


def test_KilledExecTimeout():
    @thread_timeout(1, kill_wait=0.40)
    def killme():
        for a in range(0, 200):
            time.sleep(0.01)
        raise Exception("Not killed!")

    try:
        killme()
    except KilledExecTimeout:
        pass


def test_decorator_return():
    ''' decorator is not changing python's into inspection
    '''
    from inspect import getargspec

    def func(x, y=1, *args, **kwargs):
        return vars()

    func_with_timeout = thread_timeout(1)(func)
    assert getargspec(func) == getargspec(func_with_timeout)


def test_class_methods_are_ok():
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


def test_exceptions():
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


def test_decorator_stacking_inner():
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


def test_decorator_stacking_outer():
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


def test_waits():
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

def test_kwarg():
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
