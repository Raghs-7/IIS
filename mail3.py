import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Function to send email with an attachment
def send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path=None):
    try:
        # Set up the SMTP server (Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Create an SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)  # Login to sender's email

        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach file if provided
        if attachment_path:
            if os.path.exists(attachment_path):  # Check if file exists
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(attachment_path)}",
                    )
                    msg.attach(part)
            else:
                print("❌ Attachment file not found!")

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())

        # Close the server connection
        server.quit()

        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")



    