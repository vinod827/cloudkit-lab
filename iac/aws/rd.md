# DKIM Email Verification with Microsoft Graph API and Slack Notifications

## Overview
This project verifies DKIM signatures in emails sent via Microsoft Graph API and notifies via Slack.

## Repository Links
- **Main Code**: [test.py](https://github.com/vinod827/cloudkit-lab/blob/test/iac/aws/test.py)
- **Unit Tests**: [test_dkim_email.py](https://github.com/vinod827/cloudkit-lab/blob/test/iac/aws/test_dkim_email)

## Features
- Obtains an OAuth access token from Azure AD.
- Sends a test email via Microsoft Graph API.
- Checks if the email was received in the Outlook inbox.
- Extracts and verifies the presence of a DKIM signature.
- Sends notifications via Slack webhook.

## Setup & Installation

### Prerequisites
- Python 3.8+
- `requests` library (install using `pip install requests`)
- Microsoft Azure AD credentials
- A configured Slack webhook URL

### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/vinod827/cloudkit-lab.git
   cd cloudkit-lab/iac/aws

