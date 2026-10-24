from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent

STEPS = [
    ("Filter job posts", "recruiter_filter.py"),
    ("Validate recruiter records", "recruiter_validator.py"),
    ("Generate safe email drafts", "email_preview.py"),
    ("Review draft approvals", "approval_workflow.py"),
    ("Update follow-up tracker", "followup_tracker.py"),
    ("Generate HTML report", "report_generator.py"),
    ("Display dashboard", "dashboard.py"),
]

def main():
    print("\n=== API C2C Recruitment Automation ===")

    for label, script in STEPS:
        print(f"\n{'=' * 12} {label} {'=' * 12}")
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / script)],
            cwd=BASE_DIR,
            check=False,
        )

        if result.returncode != 0:
            print(f"\nStopped: {script} returned an error.")
            print("Fix the error and rerun python main.py.")
            return

    print("\nWorkflow completed successfully.")
    print("Email sending was not performed.")
    print(f"Report: {BASE_DIR / 'reports' / 'recruitment_report.html'}")

if __name__ == "__main__":
    main()
