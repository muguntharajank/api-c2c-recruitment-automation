
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "sample_posts.csv"
OUTPUT_FILE = BASE_DIR / "data" / "filtered_posts.csv"

# Required recruitment keywords
KEYWORDS = (
    "JAVA DEVELOPER",
    "JAVA ENGINEER",
    "BENCH",
    "SALES",
    "W2",
    "FULL-TIME",
    "FULL TIME",
    "HOTLIST",
)

CONTRACT_KEYWORDS = (
    "C2C",
    "CORP TO CORP",
    "CONTRACT",
)

US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE",
    "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
    "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC",
}


def is_us_location(location):
    text = str(location).upper().strip()

    if "USA" in text or "UNITED STATES" in text:
        return True

    parts = text.replace(",", " ").split()

    # Examples: "Dallas TX", "Chicago IL"
    return any(part in US_STATE_CODES for part in parts)


def is_relevant(row, cutoff, now):
    title = str(row.get("job_title", "")).upper()
    description = str(row.get("description", "")).upper()
    combined = f"{title} {description}"

    posted = pd.to_datetime(row.get("posted_at"), errors="coerce")

    if pd.isna(posted):
        return False

    # Handle timezone-aware timestamps
    if posted.tzinfo is not None:
        posted = posted.tz_convert(None)

    posted_time = posted.to_pydatetime()

    if posted_time < cutoff or posted_time > now:
        return False

    if not is_us_location(row.get("location", "")):
        return False

    # Match at least one requested keyword
    if not any(keyword in combined for keyword in KEYWORDS):
        return False

    # Accept relevant recruitment posts including C2C,
    # W2, full-time, bench, sales, or hotlist posts.
    employment_keywords = (
        CONTRACT_KEYWORDS
        + ("W2", "FULL-TIME", "FULL TIME", "BENCH", "SALES", "HOTLIST")
    )

    if not any(keyword in combined for keyword in employment_keywords):
        return False

    return True


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    posts = pd.read_csv(INPUT_FILE)

    required_columns = {
        "post_id", "posted_at", "location",
        "job_title", "description", "recruiter_email", "post_url",
    }

    missing = required_columns - set(posts.columns)

    if missing:
        print(f"Missing CSV columns: {', '.join(sorted(missing))}")
        return

    now = datetime.now()
    cutoff = now - timedelta(hours=24)

    mask = posts.apply(
        lambda row: is_relevant(row, cutoff, now),
        axis=1,
    )

    filtered = posts[mask].drop_duplicates(subset=["post_id"])
    filtered.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Total sample posts: {len(posts)}")
    print(f"Matching posts: {len(filtered)}")
    print(f"Saved results to: {OUTPUT_FILE}")

    if filtered.empty:
        print("No matching posts found.")
    else:
        print(
            filtered[["post_id", "job_title", "location"]]
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
