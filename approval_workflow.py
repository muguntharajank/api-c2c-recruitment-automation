
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DRAFT_FILE = BASE_DIR / "data" / "email_drafts.csv"


def main():
    if not DRAFT_FILE.exists():
        print("Draft file not found. Run email_templates.py first.")
        return

    drafts = pd.read_csv(DRAFT_FILE)

    if drafts.empty:
        print("No outreach drafts available for approval.")
        print("Reserved test emails are intentionally excluded.")
        print("No emails were sent.")
        return

    print("\nEmail Draft Approval")
    print("-" * 40)

    for index, row in drafts.iterrows():
        print(f"\nDraft {index + 1}: {row['job_title']}")
        print(f"To: {row['recruiter_email']}")
        print(f"Subject: {row['subject']}")
        print(f"Current status: {row['approval_status']}")

        choice = input("Approve this draft? (y/n, Enter to skip): ").strip().lower()

        if choice == "y":
            drafts.at[index, "approval_status"] = "APPROVED"
        elif choice == "n":
            drafts.at[index, "approval_status"] = "REJECTED"

    drafts.to_csv(DRAFT_FILE, index=False, encoding="utf-8")

    print("\nApproval statuses saved.")
    print(drafts[["post_id", "approval_status"]].to_string(index=False))
    print("No emails were sent.")


if __name__ == "__main__":
    main()
