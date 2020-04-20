IDIS
====

IDIS is a set of python / django modules that wrap around `CTP <https://mircwiki.rsna.org/index.php?title=MIRC_CTP>`_
to create an image de-identification server that uses
`DICOM Confidentiality options <http://dicom.nema.org/medical/dicom/current/output/chtml/part15/sect_E.3.html>`_.

.. image:: https://github.com/sjoerdk/idis/workflows/CI/badge.svg
   :target: https://github.com/sjoerdk/idis/actions?query=workflow%3ACI+branch%3Amaster
   :alt: Build Status
.. image:: https://codecov.io/gh/sjoerdk/idis/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/sjoerdk/idis
.. image:: https://readthedocs.org/projects/idis/badge/?version=latest
   :target: http://idis.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

* Free software: GPLv3 license
* Documentation: http://idis.readthedocs.io/


Features
--------

* Job-based de-identication that links data, user and de-identification options

* Jobs creation via django website or web API / Python client

* Pull data from local disk, network share, DICOM node or via DICOM WADO

* Uses standard `DICOM Confidentiality options <http://dicom.nema.org/medical/dicom/current/output/chtml/part15/sect_E.3.html>`_
  to define de-identification that is to be performed

Credits
-------

This package was created with Cookiecutter_ and the `pydanny/cookiecutter-django/`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`pydanny/cookiecutter-django/`:  https://github.com/pydanny/cookiecutter-django/




