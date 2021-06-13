import base64
import json
import os

import google.auth
from generate_signed_urls import generate_signed_url
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

credentials, project = google.auth.default()


def send_email(event, context):
    """
    Background Cloud Function to be triggered by Cloud Pub/Sub, which retrieves user email,
    image name and discovered text from the Pub/Sub, generates signed urls for the image
    and then sends email with signed urls and text discovered on the image

    :param event: dictionary with field 'data', which is encoded in base64 and contains dictionary with fields
    such as email, file name and message (message is the text discovered in the image)
    :param context: Metadata of triggering event
    :return: None
    """
    # retrieves data from Pub/Sub
    data = json.loads(base64.b64decode(event['data']))['data']
    email = data['email']
    file_name = data['file_name']
    discovered_text = data['message']
    FIRST_BUCKET = os.getenv("UPLOAD_BUCKET")
    SECOND_BUCKET = os.getenv("SECOND_BUCKET")
    # generates signed urls for images
    original_image_url = generate_signed_url(bucket_name=FIRST_BUCKET, object_name=file_name)
    resized_image_url = generate_signed_url(bucket_name=SECOND_BUCKET, object_name=file_name)
    # sends email
    message = Mail(
        to_emails=email,
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