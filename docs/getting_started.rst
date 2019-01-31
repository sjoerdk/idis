===============
Getting Started
===============

IDIS is a set of python / django modules that wrap around `CTP <https://mircwiki.rsna.org/index.php?title=MIRC_CTP>`_
to create an image de-identification server.

A basic CTP installation offers a de-identification pipeline which
de-identifies all files that are sent to it, or that are found in a single folder. And sends this to a single output
destination. IDIS makes it possible to define jobs. Each job has its own input, processing options and output. Jobs can
be created via django website or via a web-based rest API. This makes it possible for different users and projects to
use the same server.

To get IDIS running, :ref:`install it <installation>` and then overwrite the default :ref:`settings <settings>` where
needed.

If you want to start adding to the project yourself see :ref:`_for_developers`
