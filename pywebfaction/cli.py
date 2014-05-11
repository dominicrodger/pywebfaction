"""pywebfaction

Usage:
  pywebfaction generate_config --username=<username> --password=<password>
  pywebfaction list_emails
  pywebfaction create_email <addr>
  pywebfaction create_forwarder <addr> <fwd1>
  pywebfaction (-h | --help)
  pywebfaction --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from __future__ import print_function
from docopt import docopt
from os import path
from pywebfaction import WebFactionAPI, WebFactionFault
from six.moves import configparser
from tabulate import tabulate


def get_config_filename():
    home = path.expanduser("~")
    return path.join(home, "pywebfaction.ini")


def get_handle():
    config = configparser.RawConfigParser()
    config.read(get_config_filename())
    username = config.get('pywebfaction', 'username')
    password = config.get('pywebfaction', 'password')
    return WebFactionAPI(username, password)


def generate_config(arguments):
    config = configparser.RawConfigParser()

    config.add_section('pywebfaction')
    config.set('pywebfaction', 'username', arguments['--username'])
    config.set('pywebfaction', 'password', arguments['--password'])

    with open(get_config_filename(), 'w') as configfile:
        config.write(configfile)


def list_emails(arguments):
    api = get_handle()
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
    api = get_handle()
    response = api.create_email(arguments['<addr>'])
    print("Your mailbox name is %s, and your password is %s."
          % (response.mailbox, response.password))


def create_forwarder(arguments):
    api = get_handle()
    api.create_email_forwarder(
        arguments['<addr>'],
        [arguments['<fwd1>'], ]
    )
    print("Your email forwarder was successfully set up.")


def main():
    arguments = docopt(__doc__, version='pywebfaction 0.1.2')
    try:
        if arguments['generate_config']:
            return generate_config(arguments)
        if arguments['list_emails']:
            return list_emails(arguments)
        if arguments['create_email']:
            return create_email(arguments)
        if arguments['create_forwarder']:
            return create_forwarder(arguments)
    except configparser.NoSectionError as e:
        print("Bad configuration file - please run pywebfaction "
              "generate_config.")
    except WebFactionFault as e:
        if e.exception_message:
            print("An error occurred: %s" % e.exception_message)
        else:
            print("An unknown error occurred.")


if __name__ == '__main__':
    main()
