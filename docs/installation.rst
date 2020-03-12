.. _installation:

Installation
============

Prerequisites
-------------
This guide assumes you have python 3.7 installed an can use `PIP <https://pypi.org/project/pip/>`_.

Check out development code
--------------------------
To get a bare-bones running instance of IDIS:

1. Clone the repo

.. code-block:: console

    $ git clone https://github.com/sjoerd/idis.git

2. Install requirements

.. code-block:: console

    $ pip install -r requirements/local.txt

3. Install postgress and create a database

.. code-block:: console

    $ sudo apt install postgresql postgresql-contrib
    $ sudo -u postgres createdb idis   # create db 'idis'

4. You can then start the site by running

.. code-block:: console

    $ cd app
    $ export DATABASE_URL=postgres://postgres:postgres@localhost/idis
    $ python manage.py migrate
    $ python manage.py createsuperuser
    $ python manage.py runserver

You can then navigate to http://127.0.0.1:8000/ in your browser to see the development site.

.. _install_ctp

Install CTP
-----------
* Visit the `MIRC download site <https://mircwiki.rsna.org/index.php?title=CTP-The_RSNA_Clinical_Trial_Processor>`_
and follow the instructions there to install CTP.
* Once installed cleanly, copy the IDIS settings files and configuration over the default settings.
