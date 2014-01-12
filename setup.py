#!/usr/bin/env python

from setuptools import setup, find_packages
readme = open('README.md').read()
setup(name='pytomation',
      version='1.0',
      description='Python API for Home Automation',
      author='Jason Sharpee',
      author_email='jason@sharpee.com',
      url='http://www.github.com/zonyl/pytomation',
      packages=find_packages())
