import httpretty
import pytest
import xmlrpclib
from lxml import etree
from StringIO import StringIO
from pywebfaction import WebFactionAPI, WEBFACTION_API_ENDPOINT


def get_response_value(item):
    if isinstance(item, list):
        rval = "<value><array><data>"

        for value in item:
            rval += get_response_value(value)

        rval += "</data></array></value>"
        return rval

    if isinstance(item, basestring):
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

    with pytest.raises(xmlrpclib.Fault):
        WebFactionAPI('theuser', 'foobar')


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
                'targets': 'foobar9871',
            },
        )
    )

    api = WebFactionAPI('theuser', 'foobar')
    response = api.create_email('foo@example.org')

    assert response.password == 'password1'
    assert response.mailbox == 'foobar9871'
    assert response.email_id == 42
