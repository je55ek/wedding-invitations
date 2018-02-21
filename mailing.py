from wedding.model import party_store, Party, EmailSent
from wedding.general.store import Store
import boto3
import sys
import traceback

from invites.cli import parse_arguments, Arguments
from invites.model import build_invitations
from invites.google import get_credentials, GmailService, gmail_service
from invites.aws import upload_envelopes
from invites import render


def _create_envelopes(args: Arguments,
                      parties: Store[str, Party]):
    render_envelopes = render.EnvelopeRenderer(
        args.gimp_path,
        args.gimp_template,
        args.envelopes_dir
    )

    render_envelopes(
        parties.get_all() if len(args.only) == 0 else
        map(parties.get, args.only)
    )

    upload_envelopes(
        args.envelopes_dir,
        args.resource_bucket,
        args.envelope_prefix,
        parties
    )


def _create_emails(args: Arguments,
                   parties: Store[str, Party],
                   gmail: GmailService):
    senders_parties = filter(
        lambda party: party.inviter == args.sender,
        parties.get_all() if len(args.only) == 0 else map(parties.get, args.only)
    )

    for party in senders_parties:
        party_invitations = build_invitations(
            args.invitation_url,
            args.html_template,
            args.envelope_url_template,
            party
        )

        for invitation in party_invitations:
            try:
                draft = gmail.create_draft(render.base64_email(args.sender, invitation))
            except Exception as exc:
                print(f'Unable to create draft for party {party.id} ({party.title}): {exc}')
                traceback.print_exc()
                continue
            else:
                if args.send:
                    try:
                        gmail.send(draft)
                    except Exception as e:
                        print(f'Unable to send email for party {party.id} ({party.title}): {e}')
                        continue

        try:
            parties.modify(
                party.id,
                lambda p: p._replace(rsvp_stage = EmailSent)
            )
        except Exception as exc:
            print(f'Unable to set party {party.id} ({party.title}) rsvp stage: {exc}')


def main(args: Arguments,
         parties: Store[str, Party],
         gmail: GmailService):

    if not args.skip_envelopes:
        _create_envelopes(args, parties)

    if not args.skip_email:
        _create_emails(args, parties, gmail)


if __name__ == '__main__':
    args = parse_arguments()

    if args.send and not args.skip_email:
        answer = input("Are you sure you are ready to send invitations? (y/n): ")
        if answer.lower() != "y":
            sys.exit(0)

    parties = party_store(boto3.resource('dynamodb').Table(args.parties_table))

    if not args.skip_envelopes:
        _create_envelopes(args, parties)
    else:
        print("Skipping envelope creation because --skip-envelopes specified")

    if not args.skip_email:
        google_creds = get_credentials(
            args.client_secret_file,
            args.token_storage_file,
            render.email_address(args.sender)
        )
        _create_emails(
            args,
            parties,
            gmail_service(google_creds, args.sender)
        )
    else:
        print("Skipping email creation and sending because --skip-email specified")
