import unittest
import unittest.mock

import os
import json

import oc_mailer.Mailer

# to get rid of garbage output
import logging
logging.getLogger().propagate = False
logging.getLogger().disabled = True

class MockMIMEMultiPart(dict):
    def __init__(self, return_value):
        self._return_value = return_value
        self.attached = list()
        super().__init__

    def as_string(self):
        return self._return_value

    def attach(self, value):
        self.attached.append(value)

class MockMIMEImage():
    def __init__(self):
        pass

    def add_header(self, content_id, signature_image):
        assert(content_id == 'Content-ID')
        assert(signature_image == '<signature_image>')

class TestMailer(unittest.TestCase):
    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__config_default__oneaddr(self, mtxt, mmprt, mmimg, mhdr):
        # see we do have text message sent
        _smtp = unittest.mock.MagicMock()
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@example.com")

        # for single address
        _rv = MockMIMEMultiPart("test message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test subject"
        mtxt.return_value = "test text"

        _m.send_email("to@example.com", "Test subject", text="test text")
        mhdr.assert_called_once_with("Test subject", "utf-8")
        mtxt.assert_called_once_with("test text", "plain", "utf-8")
        mmprt.assert_called_once_with("related")
        mmimg.assert_not_called()
        _smtp.sendmail.assert_called_once_with("from@example.com", ["to@example.com"], "test message")
        self.assertEqual(_rv.get("From"), "from@example.com")
        self.assertEqual(_rv.get("Subject"), "Test subject")
        self.assertEqual(_rv.get("To"), "to@example.com")
        self.assertEqual(_rv.attached.pop(), "test text")
        
    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__config_default__twoaddr(self, mtxt, mmprt, mmimg, mhdr):
        # see we do have text message sent
        # for multiple addresses
        _smtp = unittest.mock.MagicMock()
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@example.com")

        # for single address
        _rv = MockMIMEMultiPart("test message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test subject"
        mtxt.return_value = "test text"

        _m.send_email(["to-first@example.com", "to-second@example.com"], "Test subject", text="test text")
        mhdr.assert_called_once_with("Test subject", "utf-8")
        mtxt.assert_called_once_with("test text", "plain", "utf-8")
        mmprt.assert_called_once_with("related")
        mmimg.assert_not_called()
        _smtp.sendmail.assert_called_once_with("from@example.com", 
                ["to-first@example.com", "to-second@example.com"], "test message")
        self.assertEqual(_rv.get("From"), "from@example.com")
        self.assertEqual(_rv.get("Subject"), "Test subject")
        self.assertEqual(_rv.get("To"), "to-first@example.com,to-second@example.com")
        self.assertEqual(_rv.attached.pop(), "test text")

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__config_default__twoaddr_split(self, mtxt, mmprt, mmimg, mhdr):
        # see we do have text message sent
        # for multiple addresses
        _smtp = unittest.mock.MagicMock()
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@example.com")

        # for single address
        _rv = MockMIMEMultiPart("test message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test subject"
        mtxt.return_value = "test text"

        _m.send_email(["to-first@example.com", "to-second@example.com"], "Test subject", split=True, text="test text")
        mhdr.assert_called_once_with("Test subject", "utf-8")
        mtxt.assert_called_once_with("test text", "plain", "utf-8")
        self.assertEqual(mmprt.call_count, 2)
        mmprt.assert_any_call("related")
        mmimg.assert_not_called()
        self.assertTrue(_smtp.sendmail.call_count, 2)
        _smtp.sendmail.assert_any_call("from@example.com", 
                "to-first@example.com", "test message")
        _smtp.sendmail.assert_any_call("from@example.com", 
                "to-second@example.com", "test message")
        self.assertEqual(_rv.get("From"), "from@example.com")
        self.assertEqual(_rv.get("Subject"), "Test subject")

        # the last value only should be visible due to mock limitations
        self.assertEqual(_rv.get("To"), "to-second@example.com")

        # two the same attachments should be due to mock limitations
        self.assertEqual(2, len(_rv.attached))
        self.assertEqual(_rv.attached.pop(), "test text")
        self.assertEqual(_rv.attached.pop(), "test text")

    # all other checks are done for single recipient since multi-recipient-sending is done by the same way always
    # content differs only

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__config_override__html_ddns(self, mtxt, mmprt, mmimg, mhdr):
        # default domain
        # note that it is HTML-based
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@example.com", config_path=_config_pth)

        # for single address
        _rv = MockMIMEMultiPart("test HTML message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test HTML subject"
        mtxt.return_value = "<p>test text</p>"

        _m.send_email("to@example.com", "Test HTML subject", text="test text")
        mhdr.assert_called_once_with("Test HTML subject", "utf-8")
        mtxt.assert_called_once_with('<p>The message text is: test text</p>', 'html', 'utf-8')
        mmprt.assert_called_once_with("related")
        mmimg.assert_not_called()
        _smtp.sendmail.assert_called_once_with("from@example.com", ["to@example.com"], "test HTML message")
        self.assertEqual(_rv.get("From"), "from@example.com")
        self.assertEqual(_rv.get("Subject"), "Test HTML subject")
        self.assertEqual(_rv.get("To"), "to@example.com")
        self.assertEqual(_rv.attached.pop(), "<p>test text</p>")

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__config_override__plain_sd(self, mtxt, mmprt, mmimg, mhdr):
        # exact domain, plaintext message without signature, template from configuration
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@plain.example.com", config_path=_config_pth)

        # for single address
        _rv = MockMIMEMultiPart("test PLAIN message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test PLAIN subject"
        mtxt.return_value = "test plain text"

        _m.send_email("to@example.com", "Test PLAIN subject", text="test text")
        mhdr.assert_called_once_with("Test PLAIN subject", "utf-8")
        mtxt.assert_called_once_with('Here it is:\ntest text\n', 'plain', 'utf-8')
        mmprt.assert_called_once_with("related")
        mmimg.assert_not_called()
        _smtp.sendmail.assert_called_once_with("from@plain.example.com", ["to@example.com"], "test PLAIN message")
        self.assertEqual(_rv.get("From"), "from@plain.example.com")
        self.assertEqual(_rv.get("Subject"), "Test PLAIN subject")
        self.assertEqual(_rv.get("To"), "to@example.com")
        self.assertEqual(_rv.attached.pop(), "test plain text")

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__config_override__html_sdws(self, mtxt, mmprt, mmimg, mhdr):
        # exact domain, HTML message with signature, template from configuration
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()

        # mocking signature image - it is loaded while initialization
        _rvimg = MockMIMEImage()
        mmimg.return_value = _rvimg

        _m = oc_mailer.Mailer.Mailer(_smtp, "from@html.example.com", config_path=_config_pth)

        # for single address
        _rv = MockMIMEMultiPart("<p>test HTML message from file template</p>")
        mmprt.return_value = _rv
        mhdr.return_value = "Test HTML subject"
        mtxt.return_value = "<p>test HTML text</p>"

        _m.send_email("to@example.com", "Test HTML subject", text="<p>test HTML text</p>")
        mhdr.assert_called_once_with("Test HTML subject", "utf-8")
        mtxt.assert_called_once_with(
                '<h1>Here it is</h1>\n<div><p>test HTML text</p></div>\n<img src="cid:signature_image">',
                'html', 'utf-8')
        mmprt.assert_called_once_with("related")

        # check signature is attached
        with open(_config_pth, mode='rt') as _f:
            _config = json.load(_f)

        _signature_pth = _config.get("html.example.com").get("signature_image")
        _signature_pth = os.path.join(os.path.dirname(_config_pth), _signature_pth)

        with open(_signature_pth, mode='rb') as _f:
            _signature = _f.read()

        mmimg.assert_called_once_with(_signature)

        _smtp.sendmail.assert_called_once_with("from@html.example.com", ["to@example.com"],
                "<p>test HTML message from file template</p>")
        self.assertEqual(_rv.get("From"), "from@html.example.com")
        self.assertEqual(_rv.get("Subject"), "Test HTML subject")
        self.assertEqual(_rv.get("To"), "to@example.com")
        self.assertEqual(_rv.attached.pop(), _rvimg)
        self.assertEqual(_rv.attached.pop(), "<p>test HTML text</p>")

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__override_template__plain(self, mtxt, mmprt, mmimg, mhdr):
        # custom template with many substitutes
        # exact domain, plaintext message without signature, template from configuration
        _template = "${HEADER}\n${CONTENT}"
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@plain.example.com", 
                template=_template,
                config_path=_config_pth)

        # for single address
        _rv = MockMIMEMultiPart("test PLAIN message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test PLAIN subject"
        mtxt.return_value = "test plain text"

        _m.send_email("to@example.com", "Test PLAIN subject", HEADER="the header", CONTENT="the content")
        mhdr.assert_called_once_with("Test PLAIN subject", "utf-8")
        mtxt.assert_called_once_with('the header\nthe content', 'plain', 'utf-8')
        mmprt.assert_called_once_with("related")
        mmimg.assert_not_called()
        _smtp.sendmail.assert_called_once_with("from@plain.example.com", ["to@example.com"], "test PLAIN message")
        self.assertEqual(_rv.get("From"), "from@plain.example.com")
        self.assertEqual(_rv.get("Subject"), "Test PLAIN subject")
        self.assertEqual(_rv.get("To"), "to@example.com")
        self.assertEqual(_rv.attached.pop(), "test plain text")

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__override_template__html(self, mtxt, mmprt, mmimg, mhdr):
        # custom template with many substitutes
        _template = "<h1>${HEADER}</h1><div>${CONTENT}</div>"
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@plain.example.com", 
                template=_template,
                template_type='html',
                config_path=_config_pth)

        # for single address
        _rv = MockMIMEMultiPart("test PLAIN message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test PLAIN subject"
        mtxt.return_value = "test plain text"

        _m.send_email("to@example.com", "Test PLAIN subject", HEADER="the header", CONTENT="the content")
        mhdr.assert_called_once_with("Test PLAIN subject", "utf-8")
        mtxt.assert_called_once_with('<h1>the header</h1><div>the content</div>', 'html', 'utf-8')
        mmprt.assert_called_once_with("related")
        mmimg.assert_not_called()
        _smtp.sendmail.assert_called_once_with("from@plain.example.com", ["to@example.com"], "test PLAIN message")
        self.assertEqual(_rv.get("From"), "from@plain.example.com")
        self.assertEqual(_rv.get("Subject"), "Test PLAIN subject")
        self.assertEqual(_rv.get("To"), "to@example.com")
        self.assertEqual(_rv.attached.pop(), "test plain text")
        # no signature attached
        self.assertEqual(0, len(_rv.attached))

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test_message__override_signature__html(self, mtxt, mmprt, mmimg, mhdr):
        # different signature
        # custom template with many substitutes
        _template = "<h1>${HEADER}</h1><div>${CONTENT}</div>"
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()
        _rvimg = MockMIMEImage()
        mmimg.return_value = _rvimg
        _m = oc_mailer.Mailer.Mailer(_smtp, "from@html.example.com", 
                template=_template,
                template_type='html',
                signature_image=b'signature',
                config_path=_config_pth)

        # for single address
        _rv = MockMIMEMultiPart("test PLAIN message")
        mmprt.return_value = _rv
        mhdr.return_value = "Test PLAIN subject"
        mtxt.return_value = "test plain text"

        _m.send_email("to@example.com", "Test PLAIN subject", HEADER="the header", CONTENT="the content")
        mhdr.assert_called_once_with("Test PLAIN subject", "utf-8")
        mtxt.assert_called_once_with('<h1>the header</h1><div>the content</div><img src="cid:signature_image">',
                'html', 'utf-8')
        mmprt.assert_called_once_with("related")
        mmimg.assert_called_once_with(b"signature")
        _smtp.sendmail.assert_called_once_with("from@html.example.com", ["to@example.com"], "test PLAIN message")
        self.assertEqual(_rv.get("From"), "from@html.example.com")
        self.assertEqual(_rv.get("Subject"), "Test PLAIN subject")
        self.assertEqual(_rv.get("To"), "to@example.com")
        # check signature attached
        self.assertEqual(_rv.attached.pop(), _rvimg)
        self.assertEqual(_rv.attached.pop(), "test plain text")

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test__signature_and_plain(self, mtxt, mmprt, mmimg, mhdr):
        # different signature
        # custom template with many substitutes
        _template = "${HEADER}\n${CONTENT}"
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()
        _rvimg = MockMIMEImage()
        mmimg.return_value = _rvimg

        with self.assertRaises(oc_mailer.Mailer.MailerArgumentError):
            _m = oc_mailer.Mailer.Mailer(_smtp, "from@html.xample.com", 
                    template=_template,
                    template_type='plain',
                    signature_image=b'signature',
                    config_path=_config_pth)

    @unittest.mock.patch("oc_mailer.Mailer.Header")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEImage")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEMultipart")
    @unittest.mock.patch("oc_mailer.Mailer.MIMEText")
    def test__no_sender(self, mtxt, mmprt, mmimg, mhdr):
        _template = "<h1>${HEADER}</h1><div>${CONTENT}</div>"
        _config_pth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "config.json")
        _smtp = unittest.mock.MagicMock()
        _rvimg = MockMIMEImage()
        mmimg.return_value = _rvimg

        with self.assertRaises(oc_mailer.Mailer.MailerArgumentError):
            _m = oc_mailer.Mailer.Mailer(_smtp, None, 
                    template=_template,
                    template_type='html',
                    signature_image=b'signature',
                    config_path=_config_pth)
