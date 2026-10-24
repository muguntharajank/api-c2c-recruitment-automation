import base64
import os
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

# Send-only permission: the script cannot read your inbox.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    """Authenticate with Google OAuth and return the Gmail API service."""
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            "credentials.json not found in the project folder."
        )

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES
        )
        creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def send_approved_email(to_email, subject, body):
    """Send only after the user explicitly approves the displayed draft."""
    to_email = to_email.strip()

    if not to_email or "@" not in to_email:
        raise ValueError("A valid recipient email address is required.")

    domain = to_email.rsplit("@", 1)[-1].lower()

    # Block synthetic addresses used in project sample data.
    if domain == "example.com" or domain.endswith(".example.com"):
        raise ValueError("Sending to example.com addresses is blocked.")

    message = EmailMessage()
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    print("\n========== EMAIL DRAFT ==========")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print("\n" + body)
    print("=================================")

    approval = input(
        "\nType SEND to approve this exact email, or anything else to cancel: "
    ).strip()

    if approval != "SEND":
        print("Cancelled. No email was sent.")
        return False

    # Authenticate only after explicit approval.
    service = get_gmail_service()

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    result = service.users().messages().send(
        userId="me",
        body={"raw": raw_message},
    ).execute()

    print(f"Email sent successfully. Gmail message ID: {result['id']}")
    return True


if __name__ == "__main__":
    print("Gmail OAuth sender — manual approval required.")
    print("Use a real, verified recruiter email address.")
    print("Never use synthetic example.com addresses.")

    recipient = input("Recruiter email: ").strip()
    subject = input("Email subject: ").strip()
    print("Enter the email body. Type END on a new line to finish.")

    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)

    if not subject or not "\n".join(lines).strip():
        print("Cancelled: subject and email body are required.")
    else:
        try:
            send_approved_email(recipient, subject, "\n".join(lines))
        except Exception as exc:
            print(f"Email operation failed: {type(exc).__name__}: {exc}")
