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
    httpretty.register_uri(
        httpretty.POST,
        WEBFACTION_API_ENDPOINT,
        responses=[
            httpretty.Response(
                body=generate_login_response(),
                content_type="text/xml"
            ),
            httpretty.Response(
                body=generate_response(
                    [
                        {
                            'autoresponder_from': '',
                            'autoresponse_subject': '',
                            'autoresponse_message': '',
                            'targets': ',foo@example.com',
                            'autoresponder_on': 0,
                            'email_address': 'foo@example.net',
                            'id': 72,
                        },
                        {
                            'autoresponder_from': '',
                            'autoresponse_subject': '',
                            'autoresponse_message': '',
                            'targets': 'cheesebox,foo@example.org',
                            'autoresponder_on': 0,
                            'email_address': 'bar@example.net',
                            'id': 73,
                        }
                    ]
                ),
                content_type="text/xml"
            )
        ],
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
    httpretty.register_uri(
        httpretty.POST,
        WEBFACTION_API_ENDPOINT,
        responses=[
            httpretty.Response(
                body=generate_login_response(),
                content_type="text/xml"
            ),
            httpretty.Response(
                body=generate_response(
                    {
                        'autoresponder_on': 0,
                        'script_machine': '',
                        'autoresponse_subject': '',
                        'autoresponder_from': '',
                        'script_path': '',
                        'autoresponse_message': '',
                        'email_address': 'foo@example.net',
                        'id': 72,
                        'autoresponse_from': '',
                        'targets': 'test@example.com,foo@example.com',
                    },
                ),
                content_type="text/xml"
            )
        ],
    )

    api = WebFactionAPI('theuser', 'foobar')
    api.create_email_forwarder(
        'foo@example.org',
        [
            'test@example.com',
            'bar@example.net'
        ]
    )

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
