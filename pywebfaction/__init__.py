#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pywebfaction.exceptions import WebFactionFault
from pywebfaction.mailbox_name import email_to_mailbox_name
from pywebfaction.utils import Email, EmailRequestResponse
from six.moves import xmlrpc_client


WEBFACTION_API_ENDPOINT = 'https://api.webfaction.com/'


class WebFactionAPI(object):
    def __init__(self, user, password):
        self.username = user
        self.server = xmlrpc_client.Server(WEBFACTION_API_ENDPOINT)
        try:
            self.session_id, _ = self.server.login(self.username, password)
        except xmlrpc_client.Fault as e:
            raise WebFactionFault(e)

    def list_emails(self):
        try:
            response = self.server.list_emails(self.session_id)

            return [Email(r) for r in response]
        except xmlrpc_client.Fault as e:
            raise WebFactionFault(e)

    def create_email(self, email_address):
        # Mailbox names may only contain lowercase letters, numbers
        # and _.
        mailbox_base = email_to_mailbox_name(email_address)
        mailbox = mailbox_base
        suffix = None

        while True:
            try:
                mailbox_result = self.server.create_mailbox(
                    self.session_id,
                    mailbox
                )
                break
            except xmlrpc_client.Fault as e:
                if not suffix:
                    suffix = 1
                else:
                    suffix += 1

                if suffix > 10:
                    raise WebFactionFault(e)

                mailbox = '%s%d' % (mailbox_base, suffix)

        try:
            email_result = self.server.create_email(
                self.session_id,
                email_address,
                mailbox
            )

            return EmailRequestResponse(
                mailbox,
                mailbox_result['password'],
                email_result['id'],
            )
        except xmlrpc_client.Fault as email_creation_failure:
            try:
                self.server.delete_mailbox(self.session_id, mailbox)
            except xmlrpc_client.Fault:
                raise WebFactionFault(email_creation_failure)
            raise WebFactionFault(email_creation_failure)

    def create_email_forwarder(self, email_address, forwarding_addresses):
        try:
            result = self.server.create_email(
                self.session_id,
                email_address,
                ','.join(forwarding_addresses)
            )

            return result['id']
        except xmlrpc_client.Fault as e:
            raise WebFactionFault(e)
