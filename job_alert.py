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

def fetch_jobs():
    jobs = []
    for role in KEYWORDS:
        url = f"https://www.indeed.co.in/jobs?q={role.replace(' ', '+')}&l=Pune&fromage=1"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        for job in soup.select(".job_seen_beacon")[:5]:
            title = job.select_one("h2 span")
            company = job.select_one(".companyName")
            salary = job.select_one(".salary-snippet")

            if title and company:
                sal_text = salary.text if salary else "Not specified"
                if "10" in sal_text or "LPA" in sal_text:
                    jobs.append(
                        f"{title.text.strip()} | {company.text.strip()} | {sal_text}\n{url}\n"
                    )
    return jobs

def send_email(jobs):
    if not jobs:
        body = "No >10 LPA fresher jobs found today in Pune."
    else:
        body = "\n\n".join(jobs)

    msg = MIMEText(body)
    msg["Subject"] = "Daily Pune Jobs (>10 LPA | 0–1 YOE)"
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
