import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from send_email.generate_signed_urls import generate_signed_url
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
    sga = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
    response = sga.send(message)
    # message = Mail(
    #     from_email='from_email@example.com',
    #     to_emails='to@example.com',
    #     subject='Sending with Twilio SendGrid is Fun',
    #     html_content='<strong>and easy to do anywhere, even with Python</strong>')
    # try:
    #     print(os.environ.get("SENDGRID_API_KEY"))
    #     sg = SendGridAPIClient(api_key)
    #     response = sg.send(message)
    #     print(response.status_code)
    #     print(response.body)
    #     print(response.headers)
    # except Exception as e:
    #     print(e.message)

data = {
    'email':'blomex.bloomex@gmail.com',
    'file_name':'20190702-153149-PowerSupply.png',
    'message': 'DCCT v5.2.1 - Test Report |Test Results I Power Supply Czasowy Oh 5min O Blędy 2019 16 1024x768 Pełny ekran 書 CPU Usage Temperature Power 100 70°C 140W 60°C 120W MA 50 50°C 100W 50 100 40°C SOW 30°C O GPU Usage 100 20°C 40w 10°C 20W 50 50 100 50 100 TMPINO – TMPIN1 – Package - Assembly - Assembly - Package 50 100 O Memory Ot Voltage Fan 2,5V 3000rpm 10000 2500rpm 2000rpm 50 100 1,5V 1500rpm O Frequencies 1000rpm 6000 MHz 4000 MHz 0,5V 500rpm 2000 MH O MHz OV Orpm 50 100 50 100 50 100 - CPU Frequency – GPU Frequency - CPU VCORE - VIN1 - VIN2 - VIN3 - VIN4 - CPU - GPU #0',
}
send_email(data, None)