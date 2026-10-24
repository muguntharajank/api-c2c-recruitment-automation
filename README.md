\# API C2C Recruitment \& Outreach Automation



A Python-based recruitment processing and follow-up tracking system designed to filter job posts, validate recruiter contact records, prepare outreach drafts, track follow-up statuses, and generate recruitment reports.



\## Project Overview



The system currently processes locally stored CSV data and provides a dashboard and HTML report for recruitment workflow monitoring. Safety checks exclude reserved test email addresses from outreach.



\*\*Current status:\*\* Local prototype implemented and tested. Live integrations are not yet implemented.



\## Features



\- \*\*Job Filtering:\*\* Filters job posts by configured keywords, location, and posting age.

\- \*\*Recruiter Validation:\*\* Checks email formats, missing addresses, duplicate records, and reserved test domains.

\- \*\*Email Draft Preparation:\*\* Generates draft records for eligible contacts; it does not send emails.

\- \*\*Approval Workflow:\*\* Provides a workflow for reviewing eligible outreach drafts.

\- \*\*Follow-up Tracking:\*\* Tracks outreach status, reply status, and follow-up eligibility.

\- \*\*Dashboard:\*\* Displays job, validation, draft, and follow-up statistics.

\- \*\*HTML Report:\*\* Generates a recruitment report with processing metrics and filtered job records.

\- \*\*Safety Controls:\*\* Excludes reserved `example.com` test addresses from outreach.



\## Technology Stack



\- Python

\- Pandas

\- Rich

\- Requests

\- Beautiful Soup

\- python-dotenv

\- Playwright

\- HTML and CSS



\## Project Structure



```text

API-C2C-Automation/

├── clients/

├── data/

│   ├── sample\_posts.csv

│   ├── filtered\_posts.csv

│   ├── validated\_recruiters.csv

│   ├── email\_drafts.csv

│   └── followup\_tracker.csv

├── reports/

│   └── recruitment\_report.html

├── resumes/

├── templates/

├── tests/

├── .env.example

├── .gitignore

├── approval\_workflow.py

├── dashboard.py

├── email\_preview.py

├── email\_templates.py

├── followup\_tracker.py

├── main.py

├── recruiter\_filter.py

├── recruiter\_validator.py

├── report\_generator.py

├── requirements.txt

└── README.md

```



\*Note: Some generated CSV files and directories appear only after running the relevant modules.\*



\## Prerequisites



\- Python installed on your computer

\- PowerShell or another terminal

\- A local copy of this repository



\## Installation



Open PowerShell in the project directory.



\### 1. Create a virtual environment



```powershell

python -m venv .venv

```



\### 2. Activate it



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

python -m pip install --upgrade pip

pip install -r requirements.txt

```



\## Run the Project



Run the modules in the following order:



```powershell

python recruiter\_filter.py

python recruiter\_validator.py

python email\_templates.py

python approval\_workflow.py

python followup\_tracker.py

python dashboard.py

python report\_generator.py

```



To open the generated HTML report:



```powershell

Start-Process reports\\recruitment\_report.html

```



\## Current Sample Test Results



The local sample dataset currently contains five posts.



| Metric | Result |

|---|---:|

| Sample posts | 5 |

| Matching jobs | 2 |

| Recruiter records validated | 2 |

| Reserved test email addresses | 2 |

| Email drafts generated | 0 |

| Outreach emails sent | 0 |

| Follow-ups due | 0 |



The two matching sample posts are Java Developer C2C and Senior Java Developer roles in New York and Dallas.



The test email addresses use the reserved `example.com` domain and are intentionally excluded from outreach.



\## Configuration



The `.env.example` file documents potential configuration settings, including email credentials and API keys.



For local configuration:



1\. Copy `.env.example` to `.env`.

2\. Add credentials only for integrations you have configured and are authorized to use.

3\. Never commit `.env`, passwords, app passwords, or API keys to GitHub.



The presence of a configuration variable does not mean its corresponding integration is implemented.



\## Current Limitations



The following capabilities are \*\*not yet implemented as working live integrations\*\*:



\- Live LinkedIn job-post collection

\- Verified recruiter mailbox lookup

\- Actual email delivery

\- Automatic inbox and reply detection

\- Fully automated seven-day follow-up sending

\- AI-based resume customization



The current workflow uses local CSV records. Email draft generation and follow-up tracking do not, by themselves, send messages or access an inbox.



\## Future Enhancements



\- Integrate an authorized job-post data source.

\- Add verified recruiter contact handling.

\- Implement email delivery with explicit approval and secure credentials.

\- Add authorized inbox synchronization and reply detection.

\- Automate eligible follow-up scheduling with opt-out safeguards.

\- Add unit tests and integration tests.

\- Improve reporting and error handling.



\## Safety and Privacy



\- Use authorized data sources and respect platform terms.

\- Do not store passwords or API keys in source code.

\- Verify recipient addresses and obtain approval before sending outreach.

\- Respect opt-outs and duplicate-contact safeguards.

\- Use synthetic data for testing.



\## License



Add the license appropriate for your project before publicly distributing it.



