pywebfaction
============

pywebfaction is a tool for interacting with the WebFaction API. It is
a fairly thin wrapper around the XML-RPC client, adding a few
convenience methods, and pulling out the parts of responses that
you're probably interested in.

pywebfaction is two things - an :ref:`API <api>` and a
:ref:`command-line tool <cli>`.

So far, it is only concerned with the parts of the API for handling
emails, though pull requests to change that are welcome.

Installation
------------

pywebfaction can be installed with pip::

    pip install pywebfaction

Contents
--------

.. toctree::
   :maxdepth: 2

   api
   cli
