import re

from configargparse import ArgumentTypeError, ArgParser
from wedding.model import EmailAddress


def _email_address(raw: str) -> EmailAddress:
    if len(raw) > 7:
        match = re.match(
            "^([_a-z0-9-]+(?:\.[_a-z0-9-]+)*)@([a-z0-9-]+(?:\.[a-z0-9-]+)*(?:\.[a-z]{2,4}))$",
            raw.lower()
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
        self.__rsvp_url           = args.rsvp_url
        self.__opened_url         = args.opened_url
        self.__sender             = args.sender

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
    def rsvp_url(self) -> str:
        return self.__rsvp_url

    @property
    def opened_url(self) -> str:
        return self.__opened_url

    @property
    def sender(self) -> EmailAddress:
        return self.__sender


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
        default = 'resources/template.html',
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
        '--rsvp-url',
        env_var = 'RSVP_URL',
        help = 'URL template for party RSVP. ' +
               'Must include "{partyId}" placeholder, e.g. ' +
               '"https://www.flyingjs4.life/{partyId}/rsvp"'
    )
    parser.add_argument(
        '--opened-url',
        env_var = 'OPENED_URL',
        help = 'URL template for email-opened event. ' +
               'Must include "{partyId}" placeholder, e.g. ' +
               '"https://www.flyingjs4.life/{partyId}/opened"'
    )
    parser.add_argument(
        '--sender',
        env_var = 'SENDER',
        help = 'Email address to use to send invitations.',
        type = _email_address
    )
    return Arguments(parser.parse_args())
