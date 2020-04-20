.. _for_developers:

Running the Tests
-----------------

GitHub actions is used to run the test suite on every new commit.
You can also run the tests locally by

1. In a console window make sure the database is running

.. code-block:: console

    $ ./cycle_docker_compose.sh

2. Then in a second window run

.. code-block:: console

    $ docker-compose run --rm web pytest -n 2

Replace 2 with the number of CPUs that you have on your system, this runs
the tests in parallel.

If you want to add a new test please add them to the ``app/tests`` folder.
If you only want to run the tests for a particular app, eg. for ``teams``, you can do

.. code-block:: console

    $ docker-compose run --rm web pytest -k teams_tests

Running coverage locally
------------------------

1. In a console window make sure the database is running

.. code-block:: console

    $ ./cycle_docker_compose.sh

2. Then in a second window run

.. code-block:: console

    $ docker-compose run --rm  web bash -c "COVERAGE_FILE=/tmp/cov pytest --cov-report term --cov=."