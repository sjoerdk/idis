.. IDIS documentation master file, created by
   sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

IDIS documentation
==================

IDIS is a set of python / django modules that wrap around `CTP <https://mircwiki.rsna.org/index.php?title=MIRC_CTP>`_
to create an image de-identification server.

A basic CTP installation offers a single de-identification pipeline that outputs to a single location.
IDIS extends this by grouping files in jobs. Each job has its own input, processing options and output. Jobs can
be created via django website or via a web-based rest API. This makes it possible for a single server to be used by
multiple users and projects.


Contents
========

.. toctree::
   :maxdepth: 2

   getting_started
   installation
   settings
   for_developers
   deploy


