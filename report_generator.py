
from pathlib import Path
from datetime import datetime
import html

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
REPORT_FILE = REPORT_DIR / "recruitment_report.html"


def load_csv(filename):
    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame()


def safe(value):
    return html.escape(str(value if pd.notna(value) else ""))


def count_status(df, column, value):
    if df.empty or column not in df.columns:
        return 0

    return int(
        df[column].fillna("").astype(str).str.upper().eq(value).sum()
    )


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    sample = load_csv("sample_posts.csv")
    filtered = load_csv("filtered_posts.csv")
    recruiters = load_csv("validated_recruiters.csv")
    drafts = load_csv("email_drafts.csv")
    tracker = load_csv("followup_tracker.csv")

    reserved = count_status(recruiters, "email_status", "TEST_ADDRESS")
    invalid = count_status(recruiters, "email_status", "INVALID_FORMAT")

    metrics = [
        ("Sample posts", len(sample)),
        ("Matching jobs", len(filtered)),
        ("Validated records", len(recruiters)),
        ("Email drafts", len(drafts)),
        ("Reserved test emails", reserved),
        ("Invalid email formats", invalid),
        ("Tracked recruiter records", len(tracker)),
        ("Do not contact", count_status(tracker, "outreach_status", "DO_NOT_CONTACT")),
        ("Outreach sent", count_status(tracker, "outreach_status", "SENT")),
        ("Replies received", count_status(tracker, "reply_status", "REPLIED")),
        ("Follow-ups scheduled", count_status(tracker, "followup_status", "SCHEDULED")),
        ("Follow-ups due", count_status(tracker, "followup_status", "DUE")),
    ]

    metric_cards = "\n".join(
        f'<div class="metric"><div class="label">{safe(label)}</div>'
        f'<div class="number">{value}</div></div>'
        for label, value in metrics
    )

    job_rows = []
    for _, job in filtered.iterrows():
        job_rows.append(
            "<tr>"
            f"<td>{safe(job.get('post_id', ''))}</td>"
            f"<td>{safe(job.get('job_title', ''))}</td>"
            f"<td>{safe(job.get('location', ''))}</td>"
            f"<td>{safe(job.get('posted_at', ''))}</td>"
            "</tr>"
        )

    jobs_html = "\n".join(job_rows) or (
        '<tr><td colspan="4">No matching posts</td></tr>'
    )

    tracker_rows = []
    for _, item in tracker.iterrows():
        tracker_rows.append(
            "<tr>"
            f"<td>{safe(item.get('post_id', ''))}</td>"
            f"<td>{safe(item.get('outreach_status', ''))}</td>"
            f"<td>{safe(item.get('reply_status', ''))}</td>"
            f"<td>{safe(item.get('followup_due_date', ''))}</td>"
            f"<td>{safe(item.get('followup_status', ''))}</td>"
            "</tr>"
        )

    tracker_html = "\n".join(tracker_rows) or (
        '<tr><td colspan="5">No tracking records available</td></tr>'
    )

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>API C2C Recruitment Report</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    background: #101827;
    color: #e5e7eb;
}}
main {{ max-width: 1100px; margin: 30px auto; padding: 20px; }}
header, section {{
    background: #1f2937;
    padding: 22px;
    border-radius: 12px;
    margin-bottom: 18px;
}}
h1 {{ margin-top: 0; color: #67e8f9; }}
h2 {{ color: #f3f4f6; }}
.metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
    gap: 12px;
}}
.metric {{ background: #111827; padding: 16px; border-radius: 8px; }}
.label {{ color: #9ca3af; font-size: 14px; }}
.number {{ font-size: 28px; font-weight: bold; color: #6ee7b7; margin-top: 8px; }}
.note {{ color: #fbbf24; }}
.table-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; min-width: 600px; }}
th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #374151; }}
th {{ color: #67e8f9; }}
footer {{ color: #9ca3af; font-size: 13px; padding: 10px 0; }}
</style>
</head>
<body>
<main>
<header>
<h1>API C2C Recruitment Automation</h1>
<p>Recruitment processing and follow-up report</p>
<p>Generated: {safe(generated)}</p>
</header>

<section>
<h2>Processing Summary</h2>
<div class="metrics">
{metric_cards}
</div>
</section>

<section>
<h2>Filtered Job Posts</h2>
<div class="table-wrap">
<table>
<thead><tr><th>Post ID</th><th>Job Title</th><th>Location</th><th>Posted At</th></tr></thead>
<tbody>{jobs_html}</tbody>
</table>
</div>
</section>

<section>
<h2>Recruiter Follow-up Tracker</h2>
<div class="table-wrap">
<table>
<thead>
<tr><th>Post ID</th><th>Outreach Status</th><th>Reply Status</th><th>Follow-up Due</th><th>Follow-up Status</th></tr>
</thead>
<tbody>{tracker_html}</tbody>
</table>
</div>
</section>

<section>
<h2>Safety and Limitations</h2>
<p class="note">This report generator does not send emails or access inboxes.</p>
<p>Reserved example.com addresses are excluded from outreach.</p>
<p>Data comes from local CSV files. Live LinkedIn collection and automatic reply detection are not implemented.</p>
</section>

<footer>Local development report — API C2C Recruitment Automation</footer>
</main>
</body>
</html>"""

    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"HTML report generated: {REPORT_FILE}")
    print("No emails were sent.")


if __name__ == "__main__":
    main()
