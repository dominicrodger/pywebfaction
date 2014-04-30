pywebfaction
============

pywebfaction is a tool for interacting with the WebFaction API. It is
a fairly thin wrapper around the XML-RPC client, adding a few
convenience methods, and pulling out the parts of responses that
you're probably interested in.

So far, it is only concerned with the parts of the API for handling
emails, though pull requests to change that are welcome.

.. contents:: Table of Contents
     :local:

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

Available Methods
-----------------

``list_emails``
^^^^^^^^^^^^^^^

``list_emails`` takes no arguments, and give you back a list of
objects representing the email addresses set up in your WebFaction
account, along with what they do (i.e. whether they go to a local
mailbox, or are forwarded elsewhere).

Usage is:

.. code-block:: python

    from pywebfaction import WebFactionAPI

    api = WebFactionAPI(username, password)
    emails = api.list_emails()

    for email in emails:
        print email.address
        print email.mailboxes
        print email.forwards_to


``create_email``
^^^^^^^^^^^^^^^^

``create_email`` takes an email address, and sets up a standard email
address in your WebFaction account, including creation of a local
mailbox for storing your email. It takes a single argument (the email
address to create), and returns a response object containing the
mailbox name and password (which you'll need for setting up your
email client), and the ID of the email address created.

Any errors encountered will raise the underlying ``xmlrpclib.Fault``
exception, except for the case where the provided email address is
empty, or contains no characters that are valid as part of the
generated mailbox name (in this case, ``ValueError`` will be raised).

Usage is:

.. code-block:: python

    from pywebfaction import WebFactionAPI

    api = WebFactionAPI(username, password)
    response = api.create_email('dominic@example.com')

    print response.mailbox
    print response.password
    print response.email_id

``create_email_forwarder``
^^^^^^^^^^^^^^^^^^^^^^^^^^

``create_email_forwarder`` takes two arguments - an email address to
forward emails from, and a list of email addresses to forward to, and
sets up a corresponding entry in your WebFaction account. The
returned value is the ID of the resulting email address in
WebFaction.

Usage is:

.. code-block:: python

    from pywebfaction import WebFactionAPI

    api = WebFactionAPI(username, password)
    email_id = api.create_email_forwarder(
        'dominic@example.com',
        ['barry@example.org', 'lucy@example.net', ]
    )

    print email_id
