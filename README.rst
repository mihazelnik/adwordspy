========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|
        | |landscape| |codeclimate|
    * - package
      - |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/adwordspy/badge/?style=flat
    :target: https://readthedocs.org/projects/adwordspy
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/MihaZelnik/adwordspy.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/MihaZelnik/adwordspy

.. |requires| image:: https://requires.io/github/MihaZelnik/adwordspy/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/MihaZelnik/adwordspy/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/MihaZelnik/adwordspy/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/MihaZelnik/adwordspy

.. |landscape| image:: https://landscape.io/github/MihaZelnik/adwordspy/master/landscape.svg?style=flat
    :target: https://landscape.io/github/MihaZelnik/adwordspy/master
    :alt: Code Quality Status

.. |codeclimate| image:: https://codeclimate.com/github/MihaZelnik/adwordspy/badges/gpa.svg
   :target: https://codeclimate.com/github/MihaZelnik/adwordspy
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/adwordspy.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/adwordspy

.. |downloads| image:: https://img.shields.io/pypi/dm/adwordspy.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/adwordspy

.. |wheel| image:: https://img.shields.io/pypi/wheel/adwordspy.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/adwordspy

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/adwordspy.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/adwordspy

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/adwordspy.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/adwordspy


.. end-badges

Adwords API wrapper

* Free software: BSD license

Installation
============

::

    pip install adwordspy

Documentation
=============

https://adwordspy.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
