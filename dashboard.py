
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

console = Console()


def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame()


def count_status(df, column, value):
    if df.empty or column not in df.columns:
        return 0

    return int(
        df[column].fillna("").astype(str).str.upper().eq(value).sum()
    )


def main():
    sample = load_csv("sample_posts.csv")
    filtered = load_csv("filtered_posts.csv")
    recruiters = load_csv("validated_recruiters.csv")
    drafts = load_csv("email_drafts.csv")
    tracker = load_csv("followup_tracker.csv")

    console.print(
        Panel(
            "[bold cyan]API C2C Recruitment Automation[/bold cyan]\n"
            "Recruitment & Follow-up Dashboard",
            title="Project Overview",
        )
    )

    summary = Table(title="Processing Summary")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Count", justify="right", style="green")

    summary.add_row("Sample posts loaded", str(len(sample)))
    summary.add_row("Matching jobs", str(len(filtered)))
    summary.add_row("Recruiter records validated", str(len(recruiters)))

    summary.add_row(
        "Reserved test emails",
        str(count_status(recruiters, "email_status", "TEST_ADDRESS")),
    )
    summary.add_row(
        "Invalid email formats",
        str(count_status(recruiters, "email_status", "INVALID_FORMAT")),
    )
    summary.add_row("Email drafts", str(len(drafts)))

    if not drafts.empty:
        summary.add_row(
            "Pending drafts",
            str(count_status(drafts, "approval_status", "PENDING")),
        )
        summary.add_row(
            "Approved drafts",
            str(count_status(drafts, "approval_status", "APPROVED")),
        )

    summary.add_row("Tracked recruiter records", str(len(tracker)))
    summary.add_row(
        "Do not contact",
        str(count_status(tracker, "outreach_status", "DO_NOT_CONTACT")),
    )
    summary.add_row(
        "Outreach sent",
        str(count_status(tracker, "outreach_status", "SENT")),
    )
    summary.add_row(
        "Replies received",
        str(count_status(tracker, "reply_status", "REPLIED")),
    )
    summary.add_row(
        "Follow-ups scheduled",
        str(count_status(tracker, "followup_status", "SCHEDULED")),
    )
    summary.add_row(
        "Follow-ups due",
        str(count_status(tracker, "followup_status", "DUE")),
    )

    console.print(summary)

    if not filtered.empty:
        jobs = Table(title="Filtered Job Posts")
        jobs.add_column("Post ID")
        jobs.add_column("Job Title")
        jobs.add_column("Location")

        for _, row in filtered.iterrows():
            jobs.add_row(
                str(row.get("post_id", "")),
                str(row.get("job_title", "")),
                str(row.get("location", "")),
            )

        console.print(jobs)

    console.print(
        "\n[yellow]Safety mode:[/yellow] "
        "No emails are sent. Reserved test addresses remain excluded."
    )


if __name__ == "__main__":
    main()
