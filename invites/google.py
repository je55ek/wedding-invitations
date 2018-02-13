import json
import pathlib

from apiclient import discovery
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from toolz.dicttoolz import assoc
from wedding.general.functional import option
from wedding.model import EmailAddress
from invites.render import email_address


def _get_new_credentials(client_secret_file: str):
    flow = Flow.from_client_secrets_file(
        client_secret_file,
        scopes=['https://www.googleapis.com/auth/gmail.compose'],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    auth_url, _ = flow.authorization_url(prompt='consent')

    print('Please go to this URL: {}'.format(auth_url))

    code = input('Enter the authorization code: ')
    flow.fetch_token(code=code)

    return flow.credentials


def _get_tokens(token_storage_file: str):
    if not pathlib.Path(token_storage_file).is_file():
        return {}
    with open(token_storage_file, 'r') as fin:
        return json.loads(fin.read())


def _save_tokens(token_storage_file: str, tokens):
    with open(token_storage_file, 'w') as fin:
        fin.write(json.dumps(tokens))


def get_credentials(client_secret_file: str,
                    token_storage_file: str,
                    user_id: str) -> Credentials:
    tokens = _get_tokens(token_storage_file)
    credentials = option.cata(
        Credentials,
        lambda: _get_new_credentials(client_secret_file)
    )(tokens.get(user_id))
    _save_tokens(token_storage_file, assoc(tokens, user_id, credentials.token))
    return credentials


class GmailService:
    def __init__(self, service, user_id):
        self.__service = service
        self.__user_id = user_id

    def create_draft(self,
                     message: str):
        return self.__service.users().drafts().create(
            userId = self.__user_id,
            body   = { 'message': { 'raw': message } }
        ).execute()


def gmail_service(credentials: Credentials,
                  sender: EmailAddress) -> GmailService:
    return GmailService(
        discovery.build(
            'gmail',
            'v1',
            credentials = credentials
        ),
        email_address(sender)
    )
