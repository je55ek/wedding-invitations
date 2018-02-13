from wedding.model import party_store, Party
from wedding.general.store import Store
import boto3

from invites.cli import parse_arguments, Arguments
from invites.model import build_invitations
from invites.google import get_credentials, GmailService, gmail_service
from invites import render


def main(args: Arguments,
         parties: Store[str, Party],
         gmail: GmailService):

    #invitations = (
    #    invitation
    #    for party in parties.get_all()
    #    if party.inviter == args.sender
    #    for invitation in build_invitations(
    #        args.rsvp_url,
    #        args.opened_url,
    #        args.html_template,
    #        party
    #    )
    #)

    render_envelopes = render.EnvelopeRenderer(
        args.gimp_path,
        args.gimp_template,
        '/Users/jesse/Pictures/envelopes'
    )
    render_envelopes(parties.get_all())

    #for invitation in invitations:
    #    gmail.create_draft(render.base64_email(args.sender, invitation))


if __name__ == '__main__':
    args = parse_arguments()
    google_creds = get_credentials(
        args.client_secret_file,
        args.token_storage_file,
        render.email_address(args.sender)
    )
    dynamo = boto3.resource('dynamodb')
    main(
        args,
        party_store(dynamo.Table(args.parties_table)),
        gmail_service(google_creds, args.sender)
    )
