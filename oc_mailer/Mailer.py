# coding=utf-8
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import json
import pkg_resources
import os


class Mailer(object):
    """
    Class for email notifications mailing.
    Current class is a wrapper under SMTP client. Managing of SMTP client instance must be performed in outer code.
    """

    def __init__(self, 
            smtp_client, 
            from_address, 
            template_type=None, 
            template=None, 
            signature_image=None, 
            config_path=None):
        """
        Initialize.

        :param SMTPClient smtp_client: SMTP client for mailing
        :param str from_address: Single 'from' email address
        :param str template_type: Type of email message text
        :param str template: Template string of email message text
        :param str signature_image: Raw signature image data. It may be applicable only if 'type' equals to 'html'
        """
        if not all([smtp_client, from_address]):
            raise MailerArgumentError('smtp_client, from_address - must not be empty')

        if signature_image and not template_type == 'html':
            raise MailerArgumentError('signature_image applicable only if type equals to html')

        self.__smtp = smtp_client
        self.__from_address = from_address
        self.__config_path = os.path.abspath(config_path or 
                pkg_resources.resource_filename("oc_mailer", os.path.join("resources", "config.json")))
        self.__fix_arguments(template_type, template, signature_image)

    def __fix_arguments(self, template_type, template, signature_image):
        """
        Check and fix initalization arguments

        :param str template_type: type of template ("plain", "html")
        :param str template: template for messages
        :param bytes signature_image: signature image
        """
        __config = self.__read_config()
        self.__template_type = template_type or __config.get("template_type") or "plain"

        __template_string = template or \
                __config.get("template") or \
                self.__read_from_resource(self.__config_path, __config.get("template_file")) or \
                "${text}"

        __signature_image = None
        self.__signature_image = None

        if self.__template_type == 'html':
            __signature_image = signature_image or \
                    self.__read_from_resource(self.__config_path, __config.get("signature_image"), mode='rb')

        if __signature_image:
            # we have checked above that template_type is 'html' for this case
            __template_string += '<img src="cid:signature_image">'
            self.__signature_image = MIMEImage(__signature_image)
            self.__signature_image.add_header('Content-ID', '<signature_image>')

        self.__template = Template(__template_string)


    def __read_config(self):
        """
        Read the configuration and find one suitable for mail domain of sender
        """

        with open(self.__config_path, mode='rt') as _f:
            __config = json.load(_f)

        __mail_domain = ''

        if '@' in self.__from_address:
            __mail_domain = self.__from_address.split('@', 1).pop()

        if __mail_domain not in list(__config.keys()):
            # use defaults
            __mail_domain = ""

        return __config.get(__mail_domain)

    def __read_from_resource(self, config_path, file_path, mode='rt'):
        """
        Read binary or test resource
        :param str config_path: path to a configuration
        :param str file_path: path to a file, absolute or relative to 'config_path'
        :param str mode: resouce open mode, text or binary
        """
        if not file_path:
            return None

        if not os.path.isabs(file_path):
            file_path = os.path.join(os.path.dirname(config_path), file_path)

        if not os.path.exists(file_path):
            return None

        __result = None

        with open(file_path, mode=mode) as _fl_in:
            __result = _fl_in.read()

        return __result


    def send_email(self, to_addresses, subject, split=False, **kwargs):
        """
        Send email.

        :param list to_addresses: List of str 'To' email addresses or single 'To' email address
        :param str subject: Plain text which is used as email subject
        :param str split: Defines necessity of sending separate email to each of multiple recipients
        :param kwargs: Dictionary with mapping for substitution in email message text template          
        :return: None
        """
        if not self.__smtp:
            raise MailerError('Cannot send email. Mailer is already closed.')
        if not all([to_addresses, subject]):
            raise MailerArgumentError('to_addresses and subject must not be empty')
        if not isinstance(to_addresses, list):
            to_addresses = [to_addresses]

        email_subject = Header(subject, 'utf-8')
        email_body = MIMEText(self.__template.substitute(**kwargs), self.__template_type, 'utf-8')
        if split:
            for to_address in to_addresses:
                email = self.__create_email(to_address, email_subject, email_body)
                self.__smtp.sendmail(self.__from_address, to_address, email)
        else:
            email = self.__create_email(','.join(to_addresses), email_subject, email_body)
            self.__smtp.sendmail(self.__from_address, to_addresses, email)

    def __create_email(self, to, subject, body):
        """
        Create email.

        :param str to: One or more email addresses separated by comma
        :param str subject: Email subject
        :param str body: Email body
        :return str: rendered message text
        """
        message = MIMEMultipart('related')
        message['From'] = self.__from_address
        message['To'] = to
        message['Subject'] = subject
        message.attach(body)
        if self.__signature_image:
            message.attach(self.__signature_image)
        return message.as_string()

class MailerError(Exception):
    pass


class MailerArgumentError(MailerError):
    pass
