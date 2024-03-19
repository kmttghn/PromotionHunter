import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging
import config #not a good practice I know

class Gmail():
  def __init__(self):
    # If modifying these scopes, delete the file token.json.
    self.scopes = ["https://www.googleapis.com/auth/gmail.send"]
    self.creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      self.creds = Credentials.from_authorized_user_file("token.json", self.scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        self.creds.refresh(Request())
      else:
        self.flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", self.scopes
        )
        self.creds = self.flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(self.creds.to_json())


  def send_message(self, msg):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
      service = build("gmail", "v1", credentials=self.creds)
      message = EmailMessage()

      message.set_content(msg.get("Body"))

      message["To"] = msg.get("To")
      message["From"] = msg.get("From")
      message["Subject"] = msg.get("Subject")

      # encoded message
      encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

      create_message = {"raw": encoded_message}
      # pylint: disable=E1101
      send_message = (
          service.users()
          .messages()
          .send(userId="me", body=create_message)
          .execute()
      )
      print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
      print(f"An error occurred: {error}")
      send_message = None
    return send_message


if __name__ == "__main__":
  logging.basicConfig(
      handlers=[
          logging.StreamHandler()
      ],
      level=logging.INFO, 
      format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %H:%M:%S"
  )
  message = {"To": config.MESSAGE_TO,
            "From": config.MESSAGE_FROM,
            "Subject":f"Default subject",
            "Body": "Automated message"}
  gmail = Gmail()
  gmail.send_message(message)