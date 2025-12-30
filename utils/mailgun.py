# where is requests?
import requests
import os
import dotenv
dotenv.load_dotenv()


def send_message(to, subject, body):
  print('check: ',os.getenv('MAILGUN_URL', 'MAILGUN_URL'))
  return requests.post(
    f"{os.getenv('MAILGUN_URL', 'MAILGUN_URL')}/v3/{os.getenv('SANDBOX_DOMAIN', 'SANDBOX_DOMAIN')}/messages",
    auth=("api", os.getenv('MAILGUN_API_KEY', 'MAILGUN_API_KEY')),
    data={"from": f"Abdo Chaibe <postmaster@{os.getenv('SANDBOX_DOMAIN', 'SANDBOX_DOMAIN')}>",
    "to": [to],
    "subject": subject,
    "text": body})