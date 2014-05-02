import httpretty
import pytest
from lxml import etree
from six import StringIO
from six import string_types
from pywebfaction import (
    WebFactionAPI,
    WEBFACTION_API_ENDPOINT,
    email_to_mailbox_name,
    WebFactionFault
)


def get_response_value(item):
    if isinstance(item, list):
        rval = "<value><array><data>"

        for value in item:
            rval += get_response_value(value)

        rval += "</data></array></value>"
        return rval

    if isinstance(item, string_types):
        return '<value><string>%s</string></value>\n' % item

    if isinstance(item, int):
        return '<value><int>%d</int></value>\n' % item

    if isinstance(item, dict):
        rval = '<value><struct>\n'
        for key, value in item.items():
            rval += '<member>\n'
            rval += '<name>%s</name>\n' % key
            rval += get_response_value(value)
            rval += '</member>\n'
        rval += '</struct></value>\n'
        return rval

    raise NotImplementedError


def generate_response(item):
    rval = """<?xml version='1.0'?>
    <methodResponse>
    <params>
    <param>
    """

    rval += get_response_value(item)

    rval += """</param>
    </params>
    </methodResponse>
    """

    return rval


def generate_fault_response(item):
    rval = """<?xml version='1.0'?>
    <methodResponse>
    <fault>
    """

    for value in item:
        rval += get_response_value(value)

    rval += """</fault>
    </methodResponse>
    """

    return rval


def generate_login_response():
    return generate_response(
        [
            'thesession_id',
            {
                'username': 'theuser',
                'home': '/home',
                'mail_server': 'Mailbox1',
                'web_server': 'Server1',
                'id': 42
            }
        ]
    )


def register_response(*args):
    responses = [httpretty.Response(
        body=generate_login_response(),
        content_type="text/xml"
    ), ]

    responses.extend([
        httpretty.Response(
            body=r,
            content_type="text/xml"
        )
        for r in args])

    httpretty.register_uri(
        httpretty.POST,
        WEBFACTION_API_ENDPOINT,
        responses=responses,
    )


@httpretty.activate
def test_successful_login():
    httpretty.register_uri(
        httpretty.POST,
        WEBFACTION_API_ENDPOINT,
        body=generate_login_response(),
        content_type="text/xml"
    )

    api = WebFactionAPI('theuser', 'foobar')
    assert api.username == 'theuser'
    assert api.session_id == 'thesession_id'


@httpretty.activate
def test_failed_login():
    httpretty.register_uri(
        httpretty.POST,
        WEBFACTION_API_ENDPOINT,
        body=generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions'
                                    '.LoginError\'&gt;:'),
                }
            ]
        ),
        content_type="text/xml"
    )

    with pytest.raises(WebFactionFault) as excinfo:
        WebFactionAPI('theuser', 'foobar')

    assert excinfo.value.exception_type == 'LoginError'
    assert excinfo.value.exception_message is None


@httpretty.activate
def test_list_emails():
    register_response(
        generate_response(
            [
                {
                    'targets': ',foo@example.com',
                    'email_address': 'foo@example.net',
                    'id': 72,
                },
                {
                    'targets': 'cheesebox,foo@example.org',
                    'email_address': 'bar@example.net',
                    'id': 73,
                }
            ]
        )
    )

    api = WebFactionAPI('theuser', 'foobar')
    emails = api.list_emails()
    assert len(emails) == 2

    assert emails[0].address == 'foo@example.net'
    assert emails[0].mailboxes == []
    assert emails[0].forwards_to == ['foo@example.com']

    assert emails[1].address == 'bar@example.net'
    assert emails[1].mailboxes == ['cheesebox']
    assert emails[1].forwards_to == ['foo@example.org']

    # Test the request looked like we expected
    request = StringIO(httpretty.last_request().parsed_body)
    tree = etree.parse(request)
    method = tree.xpath('/methodCall/methodName')
    session = tree.xpath('/methodCall/params/param/value/string')

    assert len(method) == 1
    assert len(session) == 1
    assert method[0].text == 'list_emails'
    assert session[0].text == 'thesession_id'


@httpretty.activate
def test_list_emails_failure():
    register_response(
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ("&lt;class \'webfaction_api.exceptions."
                                    "DataError\'&gt;:[u\'We don\\\'t want to "
                                    "give you that.\']"),
                },
            ]
        ),
    )

    api = WebFactionAPI('theuser', 'foobar')
    with pytest.raises(WebFactionFault) as excinfo:
        api.list_emails()

    assert excinfo.value.exception_type == 'DataError'
    assert excinfo.value.exception_message == (
        "We don't want to give you that."
    )


@httpretty.activate
def test_create_email_forwarder():
    register_response(
        generate_response(
            {
                'email_address': 'foo@example.net',
                'id': 72,
                'targets': 'test@example.com,foo@example.com',
            },
        )
    )

    api = WebFactionAPI('theuser', 'foobar')
    email_id = api.create_email_forwarder(
        'foo@example.org',
        [
            'test@example.com',
            'bar@example.net'
        ]
    )

    assert email_id == 72

    request = StringIO(httpretty.last_request().parsed_body)
    tree = etree.parse(request)
    method = tree.xpath('/methodCall/methodName')
    parameters = tree.xpath('/methodCall/params/param/value/string')

    assert len(method) == 1
    assert len(parameters) == 3
    assert method[0].text == 'create_email'
    assert parameters[0].text == 'thesession_id'
    assert parameters[1].text == 'foo@example.org'
    assert parameters[2].text == 'test@example.com,bar@example.net'


@httpretty.activate
def test_create_email_forwarder_failure():
    register_response(
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions.'
                                    'DataError\'&gt;:[u\'Email with this '
                                    'Username and Subdomain already '
                                    'exists.\']'),
                },
            ]
        ),
    )

    api = WebFactionAPI('theuser', 'foobar')

    with pytest.raises(WebFactionFault) as excinfo:
        api.create_email_forwarder('foo@example.com', ['hello@example.net'])

    assert excinfo.value.exception_type == 'DataError'
    assert excinfo.value.exception_message == (
        'Email with this Username and Subdomain already exists.'
    )


@httpretty.activate
def test_create_email():
    register_response(
        generate_response(
            {
                'password': 'password1',
            },
        ),
        generate_response(
            {
                'email_address': 'foo@example.net',
                'id': 42,
                'targets': 'foo_exampleorg',
            },
        )
    )

    api = WebFactionAPI('theuser', 'foobar')
    response = api.create_email('foo@example.org')

    assert response.password == 'password1'
    assert response.mailbox == 'foo_exampleorg'
    assert response.email_id == 42


@httpretty.activate
def test_create_email_mailbox_exists_once():
    register_response(
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions.'
                                    'DataError\'&gt;:[u\'Mailbox with this '
                                    'Name already exists.\']'),
                },
            ]
        ),
        generate_response(
            {
                'password': 'password1',
            },
        ),
        generate_response(
            {
                'email_address': 'foo@example.net',
                'id': 42,
                'targets': 'foo_exampleorg1',
            },
        )
    )

    api = WebFactionAPI('theuser', 'foobar')
    response = api.create_email('foo@example.org')

    assert response.password == 'password1'
    assert response.mailbox == 'foo_exampleorg1'
    assert response.email_id == 42

    requests = httpretty.httpretty.latest_requests
    request = StringIO(requests[2].parsed_body)
    tree = etree.parse(request)
    params = tree.xpath('/methodCall/params/param/value/string')

    assert len(params) == 2
    assert params[1].text == 'foo_exampleorg1'


@httpretty.activate
def test_create_email_mailbox_exists_twice():
    register_response(
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions.'
                                    'DataError\'&gt;:[u\'Mailbox with this '
                                    'Name already exists.\']'),
                },
            ]
        ),
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions.'
                                    'DataError\'&gt;:[u\'Mailbox with this '
                                    'Name already exists.\']'),
                },
            ]
        ),
        generate_response(
            {
                'password': 'password1',
            },
        ),
        generate_response(
            {
                'email_address': 'foo@example.net',
                'id': 42,
                'targets': 'foo_exampleorg2',
            },
        )
    )

    api = WebFactionAPI('theuser', 'foobar')
    response = api.create_email('foo@example.org')

    assert response.password == 'password1'
    assert response.mailbox == 'foo_exampleorg2'
    assert response.email_id == 42

    requests = httpretty.httpretty.latest_requests
    request = StringIO(requests[3].parsed_body)
    tree = etree.parse(request)
    params = tree.xpath('/methodCall/params/param/value/string')

    assert len(params) == 2
    assert params[1].text == 'foo_exampleorg2'


@httpretty.activate
def test_create_email_mailbox_fails_repeatedly():
    register_response(
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions.'
                                    'DataError\'&gt;:[u\'Mailbox with this '
                                    'Name already exists.\']'),
                },
            ]
        ),
    )

    api = WebFactionAPI('theuser', 'foobar')
    with pytest.raises(WebFactionFault) as excinfo:
        api.create_email('foo@example.org')

    assert excinfo.value.exception_type == 'DataError'
    assert excinfo.value.exception_message == (
        'Mailbox with this Name already exists.'
    )


@httpretty.activate
def test_create_email_address_exists():
    register_response(
        generate_response(
            {
                'password': 'password1',
            },
        ),
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions.'
                                    'DataError\'&gt;:[u\'Email with this '
                                    'Username and Subdomain already '
                                    'exists.\']'),
                },
            ]
        ),
        # Response for delete_mailbox is fairly empty
        generate_response({}),
    )

    api = WebFactionAPI('theuser', 'foobar')
    with pytest.raises(WebFactionFault) as excinfo:
        api.create_email('foo@example.org')

    assert excinfo.value.exception_type == 'DataError'
    assert excinfo.value.exception_message == (
        'Email with this Username and Subdomain already exists.'
    )

    request = StringIO(httpretty.last_request().parsed_body)
    tree = etree.parse(request)
    method = tree.xpath('/methodCall/methodName')
    params = tree.xpath('/methodCall/params/param/value/string')

    assert len(method) == 1
    assert len(params) == 2
    assert method[0].text == 'delete_mailbox'
    assert params[0].text == 'thesession_id'
    assert params[1].text == 'foo_exampleorg'


@httpretty.activate
def test_create_email_address_exists_and_mailbox_deletion_fails():
    register_response(
        generate_response(
            {
                'password': 'password1',
            },
        ),
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions.'
                                    'DataError\'&gt;:[u\'Email with this '
                                    'Username and Subdomain already '
                                    'exists.\']'),
                },
            ]
        ),
        generate_fault_response(
            [
                {
                    'faultCode': 1,
                    'faultString': ('&lt;class \'webfaction_api.exceptions'
                                    '.DataError\'&gt;:[u\'Mailbox ist '
                                    'kaput\']'),
                }
            ]
        )
    )

    api = WebFactionAPI('theuser', 'foobar')
    with pytest.raises(WebFactionFault) as excinfo:
        api.create_email('foo@example.org')

    assert excinfo.value.exception_type == 'DataError'
    assert excinfo.value.exception_message == (
        'Email with this Username and Subdomain already exists.'
    )


def test_email_to_mailbox_all_invalid():
    with pytest.raises(ValueError):
        email_to_mailbox_name('*+@')


def test_email_to_mailbox_empty_string():
    with pytest.raises(ValueError):
        email_to_mailbox_name('')


def test_email_to_mailbox_simple():
    result = email_to_mailbox_name('foo@example.org')
    assert result == 'foo_exampleorg'


def test_email_to_mailbox_invalid_stripped():
    result = email_to_mailbox_name('foo+b@example.org')
    assert result == 'foob_exampleorg'


def test_email_to_mailbox_uppercase_lowercased():
    result = email_to_mailbox_name('FOO@example.org')
    assert result == 'foo_exampleorg'


def test_email_to_mailbox_underscores_retained():
    result = email_to_mailbox_name('foo_b@example.org')
    assert result == 'foo_b_exampleorg'


def _get_fault(message):
    class FakeFault(object):
        def __init__(self, message):
            self.faultString = message

    fake = FakeFault(message)
    return WebFactionFault(fake)


def test_exception_parsing():
    err = _get_fault(
        '<class \'webfaction_api.exceptions.DataError\'>:'
        '[u\'It all went wrong.\']'
    )

    assert err.exception_type == 'DataError'
    assert err.exception_message == 'It all went wrong.'


def test_exception_parsing_bad_type_prefix():
    err = _get_fault(
        '<class \'webfaction_api.exception.DataError\'>:'
        '[u\'It all went wrong.\']'
    )

    assert err.exception_type is None
    assert err.exception_message == 'It all went wrong.'


def test_exception_parsing_bad_type_suffix():
    err = _get_fault(
        '<class \'webfaction_api.exceptions.DataError\':'
        '[u\'It all went wrong.\']'
    )

    assert err.exception_type is None
    assert err.exception_message == 'It all went wrong.'


def test_exception_parsing_bad_length():
    err = _get_fault('')

    assert err.exception_type is None
    assert err.exception_type is None


def test_exception_parsing_message_is_not_a_list():
    err = _get_fault(
        '<class \'webfaction_api.exceptions.DataError\'>:'
        'u\'It all went wrong.\''
    )

    assert err.exception_type == 'DataError'
    assert err.exception_message is None


def test_exception_parsing_message_is_an_empty_list():
    err = _get_fault(
        '<class \'webfaction_api.exceptions.DataError\'>:'
        '[]'
    )

    assert err.exception_type == 'DataError'
    assert err.exception_message is None
