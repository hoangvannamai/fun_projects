import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_alerts(subject, text, sender_email, password, receiver_email, video_filename):
    smtp_server = "smtp.gmail.com"
    port = 587
    
    # Create a multipart message
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email
    
    # Attach the text part
    message.attach(MIMEText(text, "plain"))
    
    # Attach the video part
    with open(video_filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    name = "fire_video.mp4"
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {name}",
    )
    message.attach(part)
    
    # Send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Sent")