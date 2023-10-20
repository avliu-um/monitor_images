import boto3

from email import encoders
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email_with_attachment():
    msg = MIMEMultipart()
    msg["Subject"] = "This is an email with an attachment!"
    msg["From"] = "avliu@umich.edu"
    msg["To"] = "avliu@umich.edu"

    # Set message body
    body = MIMEText("Hello, world!", "plain")
    msg.attach(body)

    filename = "s3://ev-cloud-testing/data/data_2023-10-19_craigslist_fd79bf54-564e-4ca6-969f-f13920591e4a.json"  # In same directory as script

    with open(filename, "rb") as attachment:
        part = MIMEApplication(attachment.read())
        part.add_header("Content-Disposition",
                        "attachment",
                        filename=filename)
    msg.attach(part)

    # Convert message to string and send
    ses_client = boto3.client("ses", region_name="us-east-2")
    response = ses_client.send_raw_email(
        Source="avliu@umich.edu",
        Destinations=["avliu@umich.edu"],
        RawMessage={"Data": msg.as_string()}
    )
    print(response)

if __name__=='__main__':
    send_email_with_attachment()
