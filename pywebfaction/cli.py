"""pywebfaction

Usage:
  pywebfaction list_emails --username=<un> --password=<pw>
  pywebfaction create_email <addr> --username=<un> --password=<pw>
  pywebfaction create_forwarder <addr> <fwd1> --username=<un> --password=<pw>
  pywebfaction (-h | --help)
  pywebfaction --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from __future__ import print_function
from docopt import docopt
from pywebfaction import WebFactionAPI, WebFactionFault
from tabulate import tabulate


def get_handle(arguments):
    return WebFactionAPI(arguments['--username'],
                         arguments['--password'])


def list_emails(arguments):
    api = get_handle(arguments)
    emails = api.list_emails()
    rows = [
        (
            e.address,
            '; '.join(e.mailboxes),
            '; '.join(e.forwards_to)
        )
        for e in emails
    ]
    print(tabulate(rows, ["Email", "Mailboxes", "Forwards"]))


def create_email(arguments):
    api = get_handle(arguments)
    response = api.create_email(arguments['<addr>'])
    print("Your mailbox name is %s, and your password is %s."
          % (response.mailbox, response.password))


def create_forwarder(arguments):
    api = get_handle(arguments)
    api.create_email_forwarder(
        arguments['<addr>'],
        [arguments['<fwd1>'], ]
    )
    print("Your email forwarder was successfully set up.")


def main():
    arguments = docopt(__doc__, version='pywebfaction 0.1.0')
    try:
        if arguments['list_emails']:
            return list_emails(arguments)
        if arguments['create_email']:
            return create_email(arguments)
        if arguments['create_forwarder']:
            return create_forwarder(arguments)
    except WebFactionFault as e:
        if e.exception_message:
            print("An error occurred: %s" % e.exception_message)
        else:
            print("An unknown error occurred.")


if __name__ == '__main__':
    main()
