#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    def create_email(self, email_address):
        # Need to generate a mailbox name (may only contain lowercase
        # letters, numbers and _)
        mailbox = 'foobar9871'
        result = self.server.create_mailbox(
            self.session_id,
            mailbox
        )

        print "Password for the new mailbox is: %s" % result['password']

        try:
            self.server.create_email(
                self.session_id,
                email_address,
                mailbox
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
