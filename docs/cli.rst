.. _cli:

Command-line Usage
==================

Once pywebfaction is installed, a command-line tool is available
called ``pywebfaction``, running it will print the help message::

    Usage:
      pywebfaction list_emails --username=<un> --password=<pw>
      pywebfaction create_email <address>
      pywebfaction create_email_forwarder <address> <forward_to1>
      pywebfaction (-h | --help)
      pywebfaction --version

The command ``list_emails`` will print a table showing what emails
are set up on your WebFaction account.

The command ``create_email`` will set you up an email address and a
corresponding mailbox, and tell you what the name of the mailbox
created was, and what password was set up for it. The information
printed out should be all you need to follow WebFaction's
instructions for `configuring email clients
<http://docs.webfaction.com/user-guide/email_clients/other.html>`_.

The command ``create_email_forwarder`` will set up an email address
which forwards to another email address (the forwarding address can
be any email address, not necessarily one on WebFaction).
