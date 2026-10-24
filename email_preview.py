from pathlib import Path
import re
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "filtered_posts.csv"
HISTORY_FILE = BASE_DIR / "data" / "email_sent_history.csv"
DRAFT_FILE = BASE_DIR / "data" / "email_drafts.csv"

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def valid_email(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not EMAIL_PATTERN.fullmatch(value):
        return False
    # Reserved domain: sample records must never be emailed.
    if value.lower().endswith("@example.com"):
        return False
    return True


def main():
    if not INPUT_FILE.exists():
        print("Filtered posts not found. Run recruiter_filter.py first.")
        return

    posts = pd.read_csv(INPUT_FILE)

    if HISTORY_FILE.exists():
        history = pd.read_csv(HISTORY_FILE)
        sent_ids = set(history.get("post_id", pd.Series(dtype=str)).astype(str))
    else:
        sent_ids = set()

    drafts = []
    skipped_email = 0
    skipped_duplicate = 0

    for _, row in posts.iterrows():
        post_id = str(row["post_id"])
        email = str(row.get("recruiter_email", "")).strip()

        if post_id in sent_ids:
            skipped_duplicate += 1
            continue

        if not valid_email(email):
            skipped_email += 1
            continue

        drafts.append({
            "post_id": post_id,
            "recruiter_email": email,
            "job_title": row["job_title"],
            "post_url": row["post_url"],
            "subject": f"Interest in {row['job_title']} opportunity",
            "body": (
                f"Hello,\n\n"
                f"I came across your post about {row['job_title']} "
                f"and would like to learn more about the opportunity.\n\n"
                f"Could you please share the job description and requirements?\n\n"
                f"Thank you."
            ),
            "approval_status": "PENDING"
        })

    columns = [
        "post_id", "recruiter_email", "job_title", "post_url",
        "subject", "body", "approval_status"
    ]
    pd.DataFrame(drafts, columns=columns).to_csv(
        DRAFT_FILE, index=False, encoding="utf-8"
    )

    print(f"Filtered posts checked: {len(posts)}")
    print(f"Drafts created: {len(drafts)}")
    print(f"Invalid/reserved emails skipped: {skipped_email}")
    print(f"Duplicate posts skipped: {skipped_duplicate}")
    print(f"Draft file: {DRAFT_FILE}")
    print("No emails were sent.")


if __name__ == "__main__":
    main()
