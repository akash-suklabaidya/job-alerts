import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]

ROLES = [
    "Software Engineer",
    "Software Developer",
    "Java Backend Developer",
    "Frontend Developer"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_indeed(role):
    urls = [
        f"https://www.indeed.co.in/jobs?q={role.replace(' ', '+')}&l=Pune",
        f"https://www.indeed.co.in/jobs?q={role.replace(' ', '+')}&remotejob=1"
    ]
    return fetch_generic(urls, "Indeed")

def fetch_simplyhired(role):
    urls = [
        f"https://www.simplyhired.co.in/search?q={role.replace(' ', '+')}&l=Pune",
        f"https://www.simplyhired.co.in/search?q={role.replace(' ', '+')}&l=Remote"
    ]
    return fetch_generic(urls, "SimplyHired")

def fetch_glassdoor(role):
    urls = [
        f"https://www.glassdoor.co.in/Job/pune-{role.replace(' ', '-')}-jobs-SRCH_IL.0,4_IC2856202_KO5,20.htm",
        f"https://www.glassdoor.co.in/Job/india-remote-{role.replace(' ', '-')}-jobs-SRCH_IL.0,5_IN115_KO6,21.htm"
    ]
    return fetch_generic(urls, "Glassdoor")

def fetch_generic(urls, source):
    jobs = []
    for url in urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")

            for a in soup.select("a[href]"):
                text = a.get_text(strip=True)
                href = a.get("href")

                if not text or not href:
                    continue

                if any(k.lower() in text.lower() for k in ["engineer", "developer", "backend", "frontend"]):
                    if href.startswith("/"):
                        href = url.split("/")[0] + "//" + url.split("/")[2] + href

                    jobs.append(f"{text} | {source}\n{href}")
        except Exception:
            continue

    return jobs

def fetch_all_jobs():
    all_jobs = []
    seen = set()

    for role in ROLES:
        sources = (
            fetch_indeed(role)
            + fetch_simplyhired(role)
            + fetch_glassdoor(role)
        )

        for job in sources:
            key = job.split("\n")[0]
            if key not in seen:
                seen.add(key)
                all_jobs.append(job)

    return all_jobs[:30]  # cap email size

def send_email(jobs):
    if not jobs:
        body = "No jobs found today across job portals."
    else:
        body = "\n\n".join(jobs)

    msg = MIMEText(body)
    msg["Subject"] = "Daily Jobs: Pune or Remote (Multi-Portal)"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    jobs = fetch_all_jobs()
    send_email(jobs)
