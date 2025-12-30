import requests
import os
import dotenv
dotenv.load_dotenv()

# to verify an email address with mailgun API
response = requests.post(
  f"https://api.mailgun.net/v5/sandbox/auth_recipients?email={os.getenv('VERIFY_EMAIL', 'NO_VERIFY_EMAIL')}",
  auth=("api", os.getenv('MAILGUN_API_KEY', 'YOUR_API_KEY'))
)

print(f"Status: {response.status_code}")