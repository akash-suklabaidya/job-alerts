import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]

KEYWORDS = [
    "Software Developer",
    "Software Engineer",
    "Java Backend Developer",
    "Frontend Developer"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def is_pune_or_remote(job):
    location = job.select_one(".companyLocation")
    if not location:
        return False

    loc_text = location.text.lower()
    return (
        "pune" in loc_text or
        "remote" in loc_text or
        "work from home" in loc_text
    )

def fetch_jobs():
    jobs = []
    seen = set()  # avoid duplicates

    for role in KEYWORDS:
        url = f"https://www.indeed.co.in/jobs?q={role.replace(' ', '+')}&fromage=1"
        res = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        for job in soup.select(".job_seen_beacon")[:15]:
            if not is_pune_or_remote(job):
                continue

            title = job.select_one("h2 span")
            company = job.select_one(".companyName")
            location = job.select_one(".companyLocation")
            link = job.find("a", href=True)

            if not (title and company and location and link):
                continue

            job_url = "https://www.indeed.co.in" + link["href"]
            key = (title.text.strip(), company.text.strip())

            if key in seen:
                continue

            seen.add(key)

            jobs.append(
                f"{title.text.strip()} | {company.text.strip()} | {location.text.strip()}\n{job_url}"
            )

    return jobs

def send_email(jobs):
    if not jobs:
        body = "No Pune or Remote jobs found today on Indeed."
    else:
        body = "\n\n".join(jobs)

    msg = MIMEText(body)
    msg["Subject"] = "Daily Jobs: Pune or Remote (Indeed)"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
