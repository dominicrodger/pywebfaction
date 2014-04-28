#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xmlrpclib


WEBFACTION_API_ENDPOINT = 'https://api.webfaction.com/'


class WebFactionAPI(object):
    def __init__(self, user, password):
        self.username = user
        self.server = xmlrpclib.Server(WEBFACTION_API_ENDPOINT, verbose=True)
        self.session_id, _ = self.server.login(self.username, password)

    def list_emails(self):
        return self.server.list_emails(self.session_id)

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
        self.server.create_email(
            self.session_id,
            email_address,
            forwarding_addresses
        )
