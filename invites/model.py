from collections import namedtuple
from typing import Iterable

import premailer
import pystache
from wedding.model import Party


Invitation = namedtuple(
    'Invitation',
    ['recipient', 'subject', 'message']
)


def build_invitations(rsvp_template: str,
                      body_template: str,
                      envelope_template: str,
                      party: Party) -> Iterable[Invitation]:
    rsvp_url     = rsvp_template    .replace('{partyId}', party.id)
    envelope_url = envelope_template.replace('{partyId}', party.id)

    return (
        Invitation(
            guest.email,
            'Jenny and Jesse are Getting Married!',
            premailer.transform(
                pystache.render(
                    body_template,
                    {
                        'partyName'  : party.title ,
                        'rsvpUrl'    : rsvp_url    ,
                        'envelopeUrl': envelope_url
                    }
                )
            )
        )
        for guest in party.guests
        if guest.email is not None
    )
