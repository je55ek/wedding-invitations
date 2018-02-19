import urllib.parse
from collections import namedtuple
from typing import Iterable
from toolz.functoolz import partial

import premailer
import pystache
from wedding.model import Party


Invitation = namedtuple(
    'Invitation',
    ['recipient', 'subject', 'message']
)


def _url_sub(field: str,
             value: str,
             url  : str) -> str:
    return url.replace(
        field,
        urllib.parse.quote(value)
    )


_substitute_party = partial(_url_sub, '{partyId}')
_substitute_guest = partial(_url_sub, '{guestId}')


def build_invitations(invitation_template: str,
                      body_template: str,
                      envelope_template: str,
                      party: Party) -> Iterable[Invitation]:
    invitation_url = _substitute_party(party.id, invitation_template)
    envelope_url   = _substitute_party(party.id, envelope_template)

    return (
        Invitation(
            guest.email,
            'Jenny and Jesse are Getting Married!',
            premailer.transform(
                pystache.render(
                    body_template,
                    {
                        'partyName'    : party.title ,
                        'invitationUrl': _substitute_guest(guest.id, invitation_url),
                        'envelopeUrl'  : envelope_url
                    }
                )
            )
        )
        for guest in party.guests
        if guest.email is not None
    )
