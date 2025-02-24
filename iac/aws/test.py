from exchangelib import Credentials, Account

# Set up credentials
email = ""
password = ""

# Connect to the mailbox
credentials = Credentials(email, password)
account = Account(email, credentials=credentials, autodiscover=True)

# Fetch the latest emails
for item in account.inbox.all().order_by('-datetime_received')[:5]:
    print(f"Subject: {item.subject}, Sender: {item.sender}, Date: {item.datetime_received}")



import requests

# Azure AD Credentials
TENANT_ID = "your_tenant_id"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
USER_EMAIL = "your_outlook_email@outlook.com"

# Get OAuth2 token
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
token_data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET",
    "scope": "https://graph.microsoft.com/.default",
}
token_response = requests.post(token_url, data=token_data)
token_json = token_response.json()
access_token = token_json.get("access_token")

if not access_token:
    print("Failed to obtain access token:", token_json)
    exit()

# Read emails using Microsoft Graph API
email_url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/mailFolders/Inbox/messages?$top=5"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
}

response = requests.get(email_url, headers=headers)

if response.status_code == 200:
    emails = response.json().get("value", [])
    print("\n📧 Latest Emails:\n")
    for email in emails:
        print(f"🔹 From: {email['from']['emailAddress']['name']} ({email['from']['emailAddress']['address']})")
        print(f"📌 Subject: {email['subject']}")
        print(f"📅 Received: {email['receivedDateTime']}")
        print(f"📨 Preview: {email['bodyPreview'][:200]}\n")  # Show preview (limit to 200 chars)
else:
    print("Failed to fetch emails:", response.json())
