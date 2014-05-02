===============================
PyWebFaction
===============================

A tool for interacting with the WebFaction API.

Documentation is available on `Read the Docs
<http://pywebfaction.readthedocs.org/>`_.

Installation
------------

pywebfaction can be installed with pip::

    pip install pywebfaction

Basic Usage
-----------

The API is interacted with via the class ``WebFactionAPI``, which
takes a username and password, and connects to WebFaction for you.

.. code-block:: python

    from pywebfaction import WebFactionAPI

    api = WebFactionAPI(username, password)
    emails = api.list_emails()
