import re
import string
from typing import List

from configargparse import ArgumentTypeError, ArgParser
from wedding.model import EmailAddress


def parse_email_address(raw: str) -> EmailAddress:
    if len(raw) > 7:
        match = re.match(
            "^([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$",
            raw.lower().lstrip(string.whitespace).rstrip(string.whitespace)
        )
        if match:
            return EmailAddress(match.group(1), match.group(2))
    raise ArgumentTypeError(f'{raw} is not a valid email address')


def _template(filename: str) -> str:
    try:
        with open(filename, 'r') as fin:
            return fin.read()
    except FileNotFoundError:
        raise ArgumentTypeError(f'{filename} does not exist')


class Arguments:
    def __init__(self, args):
        self.__parties_table      = args.parties_table
        self.__client_secret_file = args.client_secret_file
        self.__token_storage_file = args.token_storage_file
        self.__html_template      = args.html_template
        self.__gimp_path          = args.gimp_path
        self.__gimp_template      = args.gimp_template
        self.__invitation_url     = args.invitation_url
        self.__sender             = args.sender
        self.__envelopes_dir      = args.envelopes_dir
        self.__envelope_url       = args.envelope_url_template
        self.__resource_bucket    = args.resource_bucket
        self.__envelope_prefix    = args.envelope_prefix
        self.__send               = args.send
        self.__skip_envelopes     = args.skip_envelopes
        self.__skip_email         = args.skip_email
        self.__only               = args.only

    @property
    def parties_table(self) -> str:
        return self.__parties_table

    @property
    def client_secret_file(self) -> str:
        return self.__client_secret_file

    @property
    def token_storage_file(self) -> str:
        return self.__token_storage_file

    @property
    def html_template(self) -> str:
        return self.__html_template

    @property
    def gimp_path(self) -> str:
        return self.__gimp_path

    @property
    def gimp_template(self) -> str:
        return self.__gimp_template

    @property
    def invitation_url(self) -> str:
        return self.__invitation_url

    @property
    def sender(self) -> EmailAddress:
        return self.__sender

    @property
    def envelopes_dir(self) -> str:
        return self.__envelopes_dir

    @property
    def envelope_url_template(self) -> str:
        return self.__envelope_url

    @property
    def resource_bucket(self) -> str:
        return self.__resource_bucket

    @property
    def envelope_prefix(self) -> str:
        return self.__envelope_prefix

    @property
    def send(self) -> bool:
        return self.__send

    @property
    def skip_envelopes(self) -> bool:
        return self.__skip_envelopes

    @property
    def skip_email(self) -> bool:
        return self.__skip_email

    @property
    def only(self) -> List[str]:
        return self.__only


def parse_arguments() -> Arguments:
    parser = ArgParser(default_config_files=['settings.conf'])
    parser.add_argument(
        '--parties-table',
        env_var = 'PARTIES_TABLE'
    )
    parser.add_argument(
        '--client-secret-file',
        default = 'secrets/client_secret.json',
        env_var = 'CLIENT_SECRET_FILE'
    )
    parser.add_argument(
        '--token-storage-file',
        default = 'secrets/tokens.json',
        env_var = 'TOKEN_STORAGE_FILE'
    )
    parser.add_argument(
        '--html-template',
        default = 'resources/email_template.html',
        env_var = 'TEMPLATE',
        type    = _template
    )
    parser.add_argument(
        '--gimp-path',
        default = '/Applications/GIMP.app/Contents/MacOS/GIMP',
        env_var = 'GIMP_PATH'
    )
    parser.add_argument(
        '--gimp-template',
        env_var = 'GIMP_TEMPLATE'
    )
    parser.add_argument(
        '--invitation-url',
        env_var = 'RSVP_URL',
        help = 'URL template for party RSVP. ' +
               'Must include "{partyId}" and "{guestId}" placeholders, e.g. ' +
               '"https://www.flyingjs4.life/invitation?party={partyId}&guest={guestId}"'
    )
    parser.add_argument(
        '--sender',
        env_var = 'SENDER',
        help = 'Email address to use to send invitations.',
        type = parse_email_address
    )
    parser.add_argument(
        '--envelopes-dir',
        env_var = 'ENVELOPES_DIR',
        help = 'Directory where envelope images will be saved.'
    )
    parser.add_argument(
        '--resource-bucket',
        env_var = 'RESOURCE_BUCKET',
        help = 'Name of S3 bucket where static resources are stored.'
    )
    parser.add_argument(
        '--envelope-prefix',
        env_var = 'ENVELOPE_PREFIX',
        help = 'Prefix of all envelope objects in resource bucket.'
    )
    parser.add_argument(
        '--envelope-url-template',
        env_var = 'ENVELOPE_URL_TEMPLATE',
        help = 'URL template for envelope images. ' +
               'Must include "{partyId}" placeholder, e.g. ' +
               '"https://www.flyingjs4.life/envelopes/{partyId}.png"'
    )
    parser.add_argument(
        '--send',
        action = 'store_true',
        help = 'Send emails. USE ONLY WHEN ABSOLUTELY READY TO INVITE EVERYONE!'
    )
    parser.add_argument(
        '--skip-envelopes',
        action = 'store_true',
        help = 'Do not render envelopes'
    )
    parser.add_argument(
        '--skip-email',
        action = 'store_true',
        help = 'Do not create or send email invitations'
    )
    parser.add_argument(
        '--only',
        action = 'append',
        help = 'Only operate on the parties with these IDs',
        default = []
    )
    return Arguments(parser.parse_args())
