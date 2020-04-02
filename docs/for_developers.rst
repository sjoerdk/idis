.. _for_developers:

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

    $ test -k teams_tests
