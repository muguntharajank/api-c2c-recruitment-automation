
from pathlib import Path
import re

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "filtered_posts.csv"
OUTPUT_FILE = BASE_DIR / "data" / "validated_recruiters.csv"

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def validate_email(value):
    if pd.isna(value):
        return "MISSING"

    email = str(value).strip()

    if not EMAIL_PATTERN.fullmatch(email):
        return "INVALID_FORMAT"

    # Reserved testing addresses must never be contacted.
    if email.lower().endswith("@example.com"):
        return "TEST_ADDRESS"

    return "FORMAT_VALID_REQUIRES_VERIFICATION"


def main():
    if not INPUT_FILE.exists():
        print("Filtered posts not found. Run recruiter_filter.py first.")
        return

    df = pd.read_csv(INPUT_FILE)

    required = {"post_id", "recruiter_email", "job_title", "post_url"}
    missing = required - set(df.columns)

    if missing:
        print("Missing columns:", ", ".join(sorted(missing)))
        return

    df["email_status"] = df["recruiter_email"].apply(validate_email)

    duplicate_mask = df.duplicated(subset=["post_id"], keep="first")
    df["duplicate_post"] = duplicate_mask

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Recruiter records checked: {len(df)}")
    print(f"Reserved test addresses: {(df['email_status'] == 'TEST_ADDRESS').sum()}")
    print(f"Invalid email formats: {(df['email_status'] == 'INVALID_FORMAT').sum()}")
    print(f"Missing emails: {(df['email_status'] == 'MISSING').sum()}")
    print(f"Duplicate posts: {int(duplicate_mask.sum())}")
    print(f"Saved report: {OUTPUT_FILE}")
    print("Note: format-valid does not mean the mailbox is verified.")


if __name__ == "__main__":
    main()
