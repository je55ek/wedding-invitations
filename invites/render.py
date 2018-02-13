import base64
import json
import os
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tempfile import TemporaryDirectory
from typing import Iterable, TextIO

from wedding.model import EmailAddress, Party

from invites.model import Invitation


class EnvelopeRenderer:
    def __init__(self,
                 gimp_path    : str,
                 template_file: str,
                 output_dir   : str) -> None:
        self.__gimp_path     = os.path.abspath(gimp_path)
        self.__template_file = os.path.abspath(template_file)
        self.__output_dir    = os.path.abspath(output_dir)

    @staticmethod
    def write_recipients_file(recipients: Iterable[Party],
                              file: TextIO) -> None:
        file.write(
            json.dumps({
                'recipients': [
                    {
                        'title': recipient.title,
                        'id'   : recipient.id
                    }
                    for recipient in recipients
                ]
            })
        )

    def __command(self, recipients_file: str) -> str:
        args = f'"{self.__template_file}" "{recipients_file}" "{self.__output_dir}"'
        return \
            f"""{self.__gimp_path} \\
            --no-interface \\
            --batch '(python-fu-invite-gen RUN-NONINTERACTIVE {args})' \\
            --batch '(gimp-quit 1)'"""

    def __call__(self, recipients: Iterable[Party]) -> int:
        if not os.path.exists(self.__output_dir):
            os.makedirs(self.__output_dir)

        with TemporaryDirectory() as tmpdirname:
            recipients_file = os.path.join(tmpdirname, 'recipients.json')

            with open(recipients_file, 'w') as fout:
                self.write_recipients_file(recipients, fout)

            completed = subprocess.run(
                self.__command(recipients_file),
                shell = True
            )

            return completed.returncode


def email_address(address: EmailAddress) -> str:
    return f'{address.username}@{address.hostname}'


def base64_email(sender: EmailAddress,
                 invitation: Invitation) -> str:
    message = MIMEMultipart()
    message['to'] = email_address(invitation.recipient)
    message['from'] = email_address(sender)
    message['subject'] = invitation.subject
    message.preamble = """
    Your mail reader does not support HTML.
    Please visit us <a href="http://www.mysite.com">online</a>!
    """
    message.attach(MIMEText(invitation.message, _subtype='html'))

    return base64.urlsafe_b64encode(message.as_string().encode('ascii')).decode('ascii')
