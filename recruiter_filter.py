from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "sample_posts.csv"
OUTPUT_FILE = BASE_DIR / "data" / "filtered_posts.csv"
SEARCH_FILE = BASE_DIR / "data" / "linkedin_search_links.csv"

POST_AGE_HOURS = 24

ROLE_KEYWORDS = {
    "Python Developer": (
        "PYTHON DEVELOPER", "PYTHON ENGINEER", "PYTHON PROGRAMMER",
    ),
    "AI/ML Engineer": (
        "AI/ML ENGINEER", "AI ML ENGINEER", "MACHINE LEARNING ENGINEER",
        "ML ENGINEER", "AI ENGINEER", "ARTIFICIAL INTELLIGENCE ENGINEER",
    ),
    "Software Developer": (
        "SOFTWARE DEVELOPER", "SOFTWARE ENGINEER",
        "APPLICATION DEVELOPER",
    ),
}

US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

ENTRY_LEVEL_TERMS = (
    "ENTRY LEVEL", "ENTRY-LEVEL", "JUNIOR", "GRADUATE",
    "NEW GRAD", "NEW-GRAD", "FRESHER", "ASSOCIATE", "INTERN",
    "0-2 YEARS", "0 TO 2 YEARS", "1-2 YEARS",
)

SENIOR_TERMS = (
    "SENIOR", "SR.", "SR ", "LEAD", "PRINCIPAL", "STAFF ENGINEER",
    "DIRECTOR", "MANAGER",
)


def is_us_location(location):
    text = str(location).upper().strip()

    if "USA" in text or "UNITED STATES" in text:
        return True

    parts = text.replace(",", " ").split()
    return any(part in US_STATE_CODES for part in parts)


def get_role_match(title, description):
    title = str(title).upper()
    description = str(description).upper()

    # Prefer the job title over keywords mentioned only in the description.
    for role, keywords in ROLE_KEYWORDS.items():
        if any(keyword in title for keyword in keywords):
            return role

    for role, keywords in ROLE_KEYWORDS.items():
        if any(keyword in description for keyword in keywords):
            return role

    return ""


def assess_experience(title, description):
    text = f"{title} {description}".upper()

    if any(term in text for term in SENIOR_TERMS):
        return "NOT_ENTRY_LEVEL", 0

    if any(term in text for term in ENTRY_LEVEL_TERMS):
        return "ENTRY_LEVEL_INDICATED", 20

    return "NOT_SPECIFIED", 10


def linkedin_search_url(role):
    params = urlencode({
        "keywords": role,
        "location": "United States",
    })
    return f"https://www.linkedin.com/jobs/search/?{params}"


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    posts = pd.read_csv(INPUT_FILE)

    required = {
        "post_id", "posted_at", "location", "job_title",
        "description", "recruiter_email", "post_url",
    }
    missing = required - set(posts.columns)

    if missing:
        print("Missing CSV columns:", ", ".join(sorted(missing)))
        return

    now = datetime.now()
    cutoff = now - timedelta(hours=POST_AGE_HOURS)
    results = []

    for _, row in posts.iterrows():
        title = str(row.get("job_title", ""))
        description = str(row.get("description", ""))
        location = str(row.get("location", ""))

        posted = pd.to_datetime(row.get("posted_at"), errors="coerce")
        if pd.isna(posted):
            continue

        if posted.tzinfo is not None:
            posted = posted.tz_convert(None)

        posted_time = posted.to_pydatetime()
        if posted_time < cutoff or posted_time > now:
            continue

        if not is_us_location(location):
            continue

        matched_role = get_role_match(title, description)
        if not matched_role:
            continue

        experience_fit, experience_points = assess_experience(
            title, description
        )

        # Explicitly senior roles are not suitable for this entry-level search.
        if experience_fit == "NOT_ENTRY_LEVEL":
            continue

        score = 60 + 20 + experience_points

        record = row.to_dict()
        record["matched_role"] = matched_role
        record["experience_fit"] = experience_fit
        record["match_score"] = score
        record["linkedin_search_url"] = linkedin_search_url(matched_role)
        results.append(record)

    columns = list(posts.columns) + [
        "matched_role", "experience_fit", "match_score",
        "linkedin_search_url",
    ]

    filtered = pd.DataFrame(results, columns=columns)
    if not filtered.empty:
        filtered = filtered.drop_duplicates(subset=["post_id"])
        filtered = filtered.sort_values(
            "match_score", ascending=False
        )

    filtered.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    search_rows = [
        {
            "target_role": role,
            "location": "United States",
            "experience_target": "Fresher / Entry-level",
            "linkedin_search_url": linkedin_search_url(role),
        }
        for role in ROLE_KEYWORDS
    ]
    pd.DataFrame(search_rows).to_csv(
        SEARCH_FILE, index=False, encoding="utf-8"
    )

    print(f"Input posts: {len(posts)}")
    print(f"Matching US posts from last {POST_AGE_HOURS} hours: {len(filtered)}")
    print(f"Saved matching jobs: {OUTPUT_FILE}")
    print(f"Saved LinkedIn search links: {SEARCH_FILE}")

    if filtered.empty:
        print("No matching sample posts found.")
    else:
        print(
            filtered[
                ["job_title", "location", "matched_role",
                 "experience_fit", "match_score"]
            ].to_string(index=False)
        )

    print("\nLinkedIn search links:")
    for role in ROLE_KEYWORDS:
        print(f"{role}: {linkedin_search_url(role)}")

    print(
        "\nNote: search links open LinkedIn. This script does not "
        "collect live LinkedIn results. A score is a ranking aid, "
        "not a guarantee of qualification."
    )


if __name__ == "__main__":
    main()
