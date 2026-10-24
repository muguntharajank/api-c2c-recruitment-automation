
from pathlib import Path
from datetime import date, datetime, timedelta

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "validated_recruiters.csv"
TRACKER_FILE = DATA_DIR / "followup_tracker.csv"

FOLLOWUP_DAYS = 7

COLUMNS = [
    "post_id",
    "recruiter_email",
    "job_title",
    "post_url",
    "email_status",
    "outreach_status",
    "outreach_date",
    "reply_status",
    "last_reply_date",
    "followup_due_date",
    "followup_status",
]


def main():
    if not INPUT_FILE.exists():
        print("Validated recruiter file not found.")
        print("Run: python recruiter_validator.py")
        return

    source = pd.read_csv(INPUT_FILE)

    required = {
        "post_id", "recruiter_email", "job_title",
        "post_url", "email_status",
    }

    missing = required - set(source.columns)
    if missing:
        print("Missing columns:", ", ".join(sorted(missing)))
        return

    # Preserve previously recorded tracking information.
    if TRACKER_FILE.exists():
        old = pd.read_csv(TRACKER_FILE, dtype=str).fillna("")
        old = old.drop_duplicates(subset=["post_id"], keep="last")
        old_records = old.set_index("post_id").to_dict("index")
    else:
        old_records = {}

    records = []

    for _, row in source.iterrows():
        post_id = str(row["post_id"])
        email_status = str(row["email_status"])
        previous = old_records.get(post_id, {})

        is_test_address = email_status == "TEST_ADDRESS"

        record = {
            "post_id": post_id,
            "recruiter_email": row["recruiter_email"],
            "job_title": row["job_title"],
            "post_url": row["post_url"],
            "email_status": email_status,
            "outreach_status": previous.get(
                "outreach_status",
                "DO_NOT_CONTACT" if is_test_address else "NOT_SENT",
            ),
            "outreach_date": previous.get("outreach_date", ""),
            "reply_status": previous.get(
                "reply_status",
                "NOT_APPLICABLE" if is_test_address else "NOT_CHECKED",
            ),
            "last_reply_date": previous.get("last_reply_date", ""),
            "followup_due_date": "",
            "followup_status": "NOT_APPLICABLE" if is_test_address else "NOT_DUE",
        }

        # Never allow reserved test addresses to become contactable.
        if is_test_address:
            record["outreach_status"] = "DO_NOT_CONTACT"
            record["reply_status"] = "NOT_APPLICABLE"
            record["followup_status"] = "NOT_APPLICABLE"
        else:
            outreach_date = str(record["outreach_date"]).strip()
            reply_status = str(record["reply_status"]).upper().strip()

            if outreach_date and record["outreach_status"] == "SENT":
                try:
                    sent_date = date.fromisoformat(outreach_date)
                    due_date = sent_date + timedelta(days=FOLLOWUP_DAYS)
                    record["followup_due_date"] = due_date.isoformat()

                    if reply_status in {"REPLIED", "OPTED_OUT"}:
                        record["followup_status"] = "STOP"
                    elif date.today() >= due_date:
                        record["followup_status"] = "DUE"
                    else:
                        record["followup_status"] = "SCHEDULED"
                except ValueError:
                    record["followup_status"] = "INVALID_OUTREACH_DATE"

        records.append(record)

    tracker = pd.DataFrame(records, columns=COLUMNS)
    tracker.to_csv(TRACKER_FILE, index=False, encoding="utf-8")

    print("\nRecruitment Follow-up Tracker")
    print("-" * 38)
    print(f"Records tracked: {len(tracker)}")
    print(
        "Do not contact: "
        f"{(tracker['outreach_status'] == 'DO_NOT_CONTACT').sum()}"
    )
    print(
        "Outreach sent: "
        f"{(tracker['outreach_status'] == 'SENT').sum()}"
    )
    print(
        "Follow-ups due: "
        f"{(tracker['followup_status'] == 'DUE').sum()}"
    )
    print(f"Saved: {TRACKER_FILE}")
    print("This tracker does not send emails or check inboxes.")


if __name__ == "__main__":
    main()
