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


Adding new dependencies
-----------------------

Poetry is used to manage the dependencies of the platform.
To add a new dependency use

.. code-block:: console

    $ poetry add <whatever>

and then commit the ``pyproject.toml`` and ``poetry.lock``.
If this is a development dependency then use the ``--dev`` flag, see the ``poetry`` documentation for more details.

Versions are unpinned in the ``pyproject.toml`` file, to update the resolved dependencies use

.. code-block:: console

    $ poetry lock

and commit the update ``poetry.lock``.
The containers will need to be rebuilt after running these steps, so stop the ``cycle_docker_compose.sh`` process with ``CTRL+C`` and restart.
