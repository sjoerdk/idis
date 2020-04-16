.. _installation:

Installation
============

Installation
------------

1. Download and install Docker

    *Linux*: Docker_ and `Docker Compose`_

    *Windows 10 Pro (Build 15063 or later)*: `Docker for Windows`_

    *Older Windows versions*: `Docker Toolbox`_

2. Clone the repo

.. code-block:: console

    $ git clone https://github.com/sjoerdk/idis
    $ cd idis

3. You can then start the site by invoking

.. code-block:: console

    $ ./cycle_docker_compose.sh

You can then navigate to https://idis.localhost in your browser to see the development site,
this is using a self-signed certificate so you will need to accept the security warning.

.. _install_ctp

Install CTP
-----------
* Visit the `MIRC download site`_
and follow the instructions there to install CTP.
* Once installed cleanly, copy the IDIS settings files and configuration over the default settings.

.. _Docker: https://docs.docker.com/install/
.. _`Docker Compose`: https://docs.docker.com/compose/install/
.. _`Docker for Windows`: https://docs.docker.com/docker-for-windows/install/
.. _`Docker Toolbox`: https://docs.docker.com/toolbox/toolbox_install_windows/
.. _`MIRC download site`: https://mircwiki.rsna.org/index.php?title=CTP-The_RSNA_Clinical_Trial_Processor
