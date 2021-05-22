import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
__package__='send_email'
from .generate_signed_urls import generate_signed_url
import os
import google.auth
credentials, project = google.auth.default()
def send_email(data, context):
    email = data['email']
    file_name = data['file_name']
    discovered_text = data['message']
    FIRST_BUCKET = os.getenv("UPLOAD_BUCKET")
    SECOND_BUCKET = os.getenv("SECOND_BUCKET")
    SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    original_image_url = generate_signed_url(service_account_file=SERVICE_ACCOUNT_FILE, bucket_name=FIRST_BUCKET, object_name=file_name)
    resized_image_url = generate_signed_url(service_account_file=SERVICE_ACCOUNT_FILE, bucket_name=SECOND_BUCKET, object_name=file_name)
    message = Mail(
        to_emails = email,
        from_email="b.jedrychowski@student.uw.edu.pl",
        subject="Text on Image - result",
        html_content=f"""
        <p> Hello {email} </p>
        <p> Recently you asked to discover text on the image {original_image_url} <p/>
        <p> We resized it to {resized_image_url} and discovered following text: </p>
        <p> {discovered_text} </p>
        <p> Thanks for using our program <p>
        """,
    )
    try:
        sga = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sga.send(message)
        print(response)
    except Exception as e:
        print(e.message)