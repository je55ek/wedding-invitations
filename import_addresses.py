import argparse
import csv
import json
import uuid
from typing import Iterable, Dict

import boto3
from toolz import reduceby, first, compose, curry
from toolz.curried import get
from wedding.general.functional import option
from wedding.model import party_store, Party, Guest, NotInvited, PartyCodec, EmailAddress

from invites.cli import parse_email_address


TITLE_FIELD   = 'Title'
EMAIL_FIELD   = 'Email'
FIRST_FIELD   = 'First'
LAST_FIELD    = 'Last'
LOCAL_FIELD   = 'Local'
INVITER_FIELD = 'Inviter'
WARNING_FIELD = 'Warning'


INVITER_MAP = {
    'Jesse': EmailAddress('jessemkelly'      , 'gmail.com'),
    'Jenny': EmailAddress('jenny.rosenberger', 'gmail.com')
}


def identity(x):
    return x


def parse_bool(s: str) -> bool:
    return s.lower() == 'true'


def main(args):
    compose(
        option.cata(post_to_database, lambda: identity)(args.parties_table),
        option.cata(write_party_json, lambda: identity)(args.write_json   ),
        parse_parties,
        read_addresses
    )(args.address_file)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address-file', default = 'addresses.csv')
    parser.add_argument('--parties-table')
    parser.add_argument('--write-json')
    return parser.parse_args()


def read_addresses(address_file: str) -> Dict[str, list]:
    with open(address_file, 'r', newline='') as fin:
        return reduceby(
            get(TITLE_FIELD),
            lambda guests, row: guests + [row],
            csv.DictReader(fin),
            []
        )


def _nonempty_email(raw_email):
    return (
        None if raw_email is None or raw_email == '' else
        parse_email_address(raw_email)
    )


def _get_inviter(party_guests) -> EmailAddress:
    inviters = set(guest[INVITER_FIELD] for guest in party_guests)
    if len(inviters) != 1:
        party_title = first(party_guests)[TITLE_FIELD]
        print(f'Party {party_title} has inviters: {inviters}')
    return INVITER_MAP[first(inviters)]


def parse_parties(records: Dict[str, list]) -> Iterable[Party]:
    for party_title, party_guests in records.items():

        yield Party(
            id    = str(uuid.uuid4()),
            title = party_title,
            local = any(
                parse_bool(guest[LOCAL_FIELD])
                for guest in party_guests
            ),
            guests = [
                Guest(
                    id         = str(uuid.uuid4()),
                    first_name = guest[FIRST_FIELD],
                    last_name  = guest[LAST_FIELD ],
                    email      = _nonempty_email(guest[EMAIL_FIELD]),
                    attending  = None,
                    rideshare  = None
                )
                for guest in party_guests
            ],
            inviter    = _get_inviter(party_guests),
            rsvp_stage = NotInvited
        )


@curry
def write_party_json(filename: str,
                     parties: Iterable[Party]) -> None:
    with open(filename, 'w') as fout:
        fout.writelines(
            map(
                compose(lambda line: line + '\n', json.dumps, PartyCodec.encode),
                parties
            )
        )


@curry
def post_to_database(table_name: str,
                     parties: Iterable[Party]) -> None:
    store = party_store(
        boto3.resource('dynamodb').Table(table_name)
    )
    store.put_all(parties)


if __name__ == '__main__':
    main(parse_arguments())
