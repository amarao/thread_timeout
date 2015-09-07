#!/usr/bin/python
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(name='thread_timeout',
          version='1.0',
          description='''Decorator to execute functionin in
            separate thread with timeout''',
          author='George Shuklin',
          author_email='george.shuklin@gmail.com',
          url='https://github.com/amarao/thread_timeout',
          packages=find_packages(),
          install_requires=['Queue', 'wrapt', 'ctypes'],
          license='LGPL',
          classifiers=[
                       "Development Status :: 4 - Beta",
                       "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                       "Topic :: Software Development :: Libraries"
          ],
          )
