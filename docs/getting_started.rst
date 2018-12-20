===============
Getting Started
===============

IDIS is a set of python / django modules that wrap around `CTP <https://mircwiki.rsna.org/index.php?title=MIRC_CTP>`_
to create an image de-identification server.

This guide assumes you have python 3.7 installed an can use `PIP <https://pypi.org/project/pip/>`_,


Installation
------------
1. Clone the repo

.. code-block:: console

    $ git clone https://github.com/sjoerd/idis.git

2. Install requirements

.. code-block:: console

    $ pip install -r requirements/local.txt

3. You can then start the site by running

.. code-block:: console

    $ cd app
    $ python manage.py migrate
    $ python manage.py runserver

You can then navigate to http://127.0.0.1:8000/ in your browser to see the development site.

Running the Tests
-----------------

TravisCI_ is used to run the test suite on every new commit.
You can also run the tests locally by

1. In a console window make sure the database is running

.. code-block:: console

    $ cd app
    $ pytest

If you want to add a new test please add them to the ``app/tests`` folder.
If you only want to run the tests for a particular app, eg. for `teams`, you can do

.. code-block:: console

    $ pytest -k teams_tests
