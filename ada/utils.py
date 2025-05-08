# Standard library import
import logging

# Third-party imports
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load from a specific file
load_dotenv(dotenv_path="config.env")


account_sid       = os.getenv("TWILIO_ACCOUNT_SID")
auth_token        = os.getenv("TWILIO_AUTH_TOKEN")
whatsapp_number   = os.getenv("TO_NUMBER")
twilio_number     = os.getenv("TWILIO_NUMBER")


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
client = Client(account_sid, auth_token)


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
        )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")