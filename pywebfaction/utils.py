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


class EmailRequestResponse(object):
    def __init__(self, mailbox, password, email_id):
        self.mailbox = mailbox
        self.password = password
        self.email_id = email_id
