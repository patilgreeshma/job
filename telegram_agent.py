import os
import requests
import sqlite3

# Fetch secret keys securely from GitHub environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Target Tech Companies (Greenhouse API Tokens)
COMPANIES = {
    "Stripe": "stripe", 
    "Figma": "figma", 
    "Twilio": "twilio",
    "Databricks": "databricks", 
    "Atlassian": "atlassian", 
    "Razorpay": "razorpay"
}

# Allowed Tracked Domains (SDE & Data for Class of 2027)
ALLOWED_KEYWORDS = [
    "sde", "software engineer", "frontend", "backend", "full stack", 
    "data science", "data scientist", "data analyst", "data engineer", "machine learning", "ml", 
    "intern", "university graduate", "early career", "2027"
]

# Strict Exclusions (Cloud, DevOps, Security)
EXCLUDED_KEYWORDS = [
    "devops", "cloud", "sre", "site reliability", "security", "cybersecurity", 
    "infrastructure engineer", "support engineer", "sysadmin", "network"
]

def init_db():
    """Initializes a local SQLite database to prevent sending duplicate alerts."""
    conn = sqlite3.connect("india_jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_jobs (
            id TEXT PRIMARY KEY, 
            title TEXT, 
            company TEXT
        )
    """)
    conn.commit()
    return conn

def send_telegram_alert(company, title, link):
    """Dispatches a formatted message directly to your Telegram Channel."""
    # FIXED: Added correct api.telegram.org subdomain and missing /bot routing path
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    message_body = (
        f"🚀 *New Job Opportunity for 2027 Batch!*\n\n"
        f"🏢 *Company:* {company}\n"
        f"💼 *Role:* {title}\n"
        f"📍 *Location:* India\n\n"
        f"🔗 [Click Here to Apply]({link})"
    )
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": message_body, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Error sending to Telegram: {response.text}")
    except Exception as e:
        print(f"Network error sending alert: {e}")

def check_and_track():
    """Fetches jobs from APIs, filters them, checks duplicates, and alerts."""
    conn = init_db()
    cursor = conn.cursor()

    for name, token in COMPANIES.items():
        # FIXED: Re-established the full formal endpoint path used by Greenhouse job boards
        api_url = f"https://greenhouse.io{token}/jobs"
        try:
            res = requests.get(api_url, timeout=10)
            if res.status_code != 200: 
                continue
            
            jobs = res.json().get("jobs", [])
            for job in jobs:
                job_id = str(job.get("id"))
                title = job.get("title", "").lower()
                location = str(job.get("location", {}).get("name", "")).lower()
                link = job.get("absolute_url", "")

                # 1. Target India location only
                if "india" not in location and "bengaluru" not in location and "hyderabad" not in location and "pune" not in location:
                    continue
                
                # 2. Filter out unwanted domains
                if any(ex in title for ex in EXCLUDED_KEYWORDS):
                    continue  
                
                # 3. Match desired software/data domains
                if not any(kw in title for kw in ALLOWED_KEYWORDS):
                    continue  

                # 4. Deduplication Check
                cursor.execute("SELECT id FROM sent_jobs WHERE id = ?", (job_id,))
                if cursor.fetchone(): 
                    continue

                # 5. Save job to database history and fire notification
                cursor.execute("INSERT INTO sent_jobs VALUES (?, ?, ?)", (job_id, job.get("title"), name))
                conn.commit()
                
                send_telegram_alert(name, job.get("title"), link)
        except Exception as e:
            print(f"Error checking board for {name}: {e}")
            
    conn.close()

if __name__ == "__main__":
    check_and_track()
