.. _cli:

Command-line Usage
==================

Once pywebfaction is installed, a command-line tool is available
called ``pywebfaction``, running it will print the help message::

    Usage:
      pywebfaction generate_config --username=<username> --password=<password>
      pywebfaction list_emails
      pywebfaction create_email <addr>
      pywebfaction create_forwarder <addr> <fwd1>
      pywebfaction (-h | --help)
      pywebfaction --version

``generate_config``
-------------------

``generate_config`` will create a file called ``pywebfaction.ini`` in
your home directory, to save you having to pass in a username and
password to every other command. Note that none of the other commands
will work if you do not have a ``pywebfaction.ini`` file in your home
directory.

``list_emails``
---------------

The command ``list_emails`` will print a table showing what emails
are set up on your WebFaction account, along with what mailboxes they
are saved to, and what addresses they forward mail to.

``create_email``
----------------

The command ``create_email`` will set you up an email address and a
corresponding mailbox, and tell you what the name of the mailbox
created was, and what password was set up for it. The information
printed out should be all you need to follow WebFaction's
instructions for `configuring email clients
<http://docs.webfaction.com/user-guide/email_clients/other.html>`_.

``create_forwarder``
--------------------

The command ``create_forwarder`` will set up an email address
which forwards to another email address (the forwarding address can
be any email address, not necessarily one on WebFaction).
