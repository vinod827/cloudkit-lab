import requests
import datetime
import time

# Azure AD Credentials
TENANT_ID = "your_tenant_id"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
USER_EMAIL = "your_outlook_email@outlook.com"

# Slack Webhook URL
SLACK_WEBHOOK_URL = "your_slack_webhook_url"

def get_access_token():
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
    }
    response = requests.post(token_url, data=token_data)
    token_json = response.json()
    return token_json.get("access_token")

def send_test_email(access_token, subject="DKIM Header Test"): 
    email_url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/sendMail"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": "This is a DKIM test email."},
            "toRecipients": [{"emailAddress": {"address": USER_EMAIL}}],
        }
    }
    response = requests.post(email_url, json=email_data, headers=headers)
    return response.status_code == 202

def check_email_received(access_token, subject):
    inbox_url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/mailFolders/Inbox/messages?$top=10"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    
    now = datetime.datetime.utcnow()
    ten_minutes_ago = now - datetime.timedelta(minutes=10)
    ten_minutes_ago_str = ten_minutes_ago.isoformat() + "Z"
    
    response = requests.get(inbox_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch emails:", response.json())
        return None
    
    emails = response.json().get("value", [])
    for email in emails:
        received_time = email["receivedDateTime"]
        subject_text = email["subject"]
        
        if subject_text == subject and received_time >= ten_minutes_ago_str:
            return email["id"]
    return None

def check_dkim_header(access_token, email_id):
    headers_url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/messages/{email_id}/internetMessageHeaders"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    
    response = requests.get(headers_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch email headers:", response.json())
        return False
    
    email_headers = response.json().get("value", [])
    for header in email_headers:
        if header["name"].lower() == "dkim-signature":
            message = "✅ DKIM signature found in email headers."
            print(message)
            send_slack_notification(message)
            return True
    
    message = "❌ DKIM signature not found."
    print(message)
    send_slack_notification(message)
    return False

def send_slack_notification(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print("Failed to send Slack notification", response.text)

if __name__ == "__main__":
    access_token = get_access_token()
    if not access_token:
        print("Failed to obtain access token")
        exit()
    
    subject = "DKIM Header Test"
    
    print("📤 Sending test email...")
    if send_test_email(access_token, subject):
        print("✅ Test email sent successfully!")
        send_slack_notification("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email")
        send_slack_notification("❌ Failed to send test email")
        exit()
    
    print("⏳ Waiting for email to arrive...")
    time.sleep(60)  # Wait 1 minute before checking inbox
    
    email_id = check_email_received(access_token, subject)
    if email_id:
        print("📩 Email received! Checking DKIM signature...")
        send_slack_notification("📩 Email received! Checking DKIM signature...")
        check_dkim_header(access_token, email_id)
    else:
        print("❌ No email received within the last 10 minutes")
        send_slack_notification("❌ No email received within the last 10 minutes")
