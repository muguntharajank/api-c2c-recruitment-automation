
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "validated_recruiters.csv"
OUTPUT_FILE = BASE_DIR / "data" / "email_drafts.csv"

TEMPLATE_SUBJECT = "Inquiry about {job_title} opportunity"

TEMPLATE_BODY = """Hello,

I came across your post about {job_title} and would like to learn more about the opportunity.

Could you please share the job description, required skills, work arrangement, and application process?

Thank you for your time.

Best regards,
[Your Name]
"""


def main():
    if not INPUT_FILE.exists():
        print("Validated recruiter file not found.")
        print("Run: python recruiter_validator.py")
        return

    df = pd.read_csv(INPUT_FILE)
    drafts = []

    for _, row in df.iterrows():
        # Never generate outreach drafts for reserved test addresses.
        if row["email_status"] != "FORMAT_VALID_REQUIRES_VERIFICATION":
            continue

        job_title = str(row["job_title"])
        drafts.append({
            "post_id": row["post_id"],
            "recruiter_email": row["recruiter_email"],
            "job_title": job_title,
            "post_url": row["post_url"],
            "subject": TEMPLATE_SUBJECT.format(job_title=job_title),
            "body": TEMPLATE_BODY.format(job_title=job_title),
            "approval_status": "PENDING",
        })

    columns = [
        "post_id",
        "recruiter_email",
        "job_title",
        "post_url",
        "subject",
        "body",
        "approval_status",
    ]

    pd.DataFrame(drafts, columns=columns).to_csv(
        OUTPUT_FILE, index=False, encoding="utf-8"
    )

    print(f"Validated records checked: {len(df)}")
    print(f"Drafts generated: {len(drafts)}")
    print(f"Saved drafts: {OUTPUT_FILE}")
    print("No emails were sent.")


if __name__ == "__main__":
    main()
