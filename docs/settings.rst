.. _settings:

========
Settings
========

.. contents::
        :local:
        :depth: 1


All permanent settings for IDIS can be set in app/config/settings/

CTP settings
============

``IDIS_CTP_INPUT_FOLDER``
--------------------------

Default: ``''`` (Empty string)

Full path to the folder that CTP reads its input files from.


``IDIS_CTP_OUTPUT_FOLDER``
--------------------------

Default: ``''`` (Empty string)

Full path to the folder that CTP writes de-identified files to.


``IDIS_PRE_FETCHING_FOLDER``
--------------------------

Default: ``''`` (Empty string)

IDIS will temporarily store input files for jobs here before passing them on to CTP.


Third party settings
====================

``FIELD_ENCRYPTION_KEY``
------------------------

Default: ``''`` (Empty string)

Secret key used by django encrypted_model_fields. See `https://pypi.org/project/django-encrypted-model-fields/`_
Used by IDIS for storing sensitive information like server passwords






