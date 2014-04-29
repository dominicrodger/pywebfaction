#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import xmlrpclib


WEBFACTION_API_ENDPOINT = 'https://api.webfaction.com/'


class WebFactionAPI(object):
    def __init__(self, user, password):
        self.username = user
        self.server = xmlrpclib.Server(WEBFACTION_API_ENDPOINT)
        self.session_id, _ = self.server.login(self.username, password)

    def list_emails(self):
        class Email(object):
            def __init__(self, entry):
                def is_mailbox(target):
                    return target.find('@') == -1

                self.address = entry['email_address']
                targets = entry['targets'].split(',')
                self.mailboxes = [e for e in targets
                                  if is_mailbox(e) and e]
                self.forwards_to = [e for e in targets
                                    if not is_mailbox(e) and e]

        response = self.server.list_emails(self.session_id)

        return [Email(r) for r in response]

    @staticmethod
    def email_to_mailbox_name(email_address):
        if not email_address:
            raise ValueError("E-mail addresses cannot be empty.")

        email_address = email_address.lower()
        valid_characters = string.ascii_letters + string.digits + '_'

        def is_valid_character(c):
            return c in valid_characters

        def make_valid(c):
            if is_valid_character(c):
                return c

            if c == '@':
                return '_'

            return ''

        joined_up = ''.join([make_valid(c) for c in email_address])

        if joined_up == '_' * len(joined_up):
            raise ValueError(
                "Mailbox names must contain at least one valid "
                "character."
            )

        return joined_up

    def create_email(self, email_address):
        # Mailbox names may only contain lowercase letters, numbers
        # and _.
        mailbox = WebFactionAPI.email_to_mailbox_name(email_address)
        mailbox_result = self.server.create_mailbox(
            self.session_id,
            mailbox
        )

        class EmailRequestResponse(object):
            def __init__(self, mailbox, password, email_id):
                self.mailbox = mailbox
                self.password = password
                self.email_id = email_id

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

        except xmlrpclib.Fault:
            self.server.delete_mailbox(self.session_id, mailbox)
            raise

    def create_email_forwarder(self, email_address, forwarding_addresses):
        result = self.server.create_email(
            self.session_id,
            email_address,
            ','.join(forwarding_addresses)
        )

        return result['id']
