import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os
import qrcode
from PIL import Image
import time

# To - do: 
# 30 8 * * 2,3,4 /path/to/your/python_environment/bin/python /path/to/your/project/cron_jobs/generate_vendor_qr.py >> /path/to/your/project/logs/generate_vendor_qr_cron.log 2>&1
# Add this to the crontab -e file and it will run every tuesday, wednesday and thursday morning 8:30



SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'your_sending_email@example.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', 'your_email_password')
QR_RECIPIENT_EMAIL = os.environ.get('QR_RECIPIENT_EMAIL', 'vendor_email@example.com')
today = datetime.date.today()
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 6000


def generate_daily_qr_data():
    daily_token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    qr_data_string = f"date={today.strftime('%Y-%m-%d')}&token={daily_token}&company=nielsen"
    print(f"Generated QR data string: {qr_data_string}")
    return qr_data_string, daily_token


def generate_qr_code_image(data_string):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        filename=f"daily_meal_qr_{today}.png"
        img.save(filename)
        print(f"QR code image saved as {filename}")
        return filename
    except Exception as e:
        print(f"Failed to generate QR code image: {e}")
        exit(1)


# --- Send Email with QR Code ---
def send_qr_email(recipient_email, qr_image_path, qr_data_string):
    subject = f"Daily Meal Redemption QR Code - {datetime.date.today().strftime('%Y-%m-%d')}"
    body = f"Please find the QR code for today's meal redemption attached.\n\nValid for {datetime.date.today().strftime('%Y-%m-%d')}.\n\nQR Data: {qr_data_string}"

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = QR_RECIPIENT_EMAIL
    msg.attach(MIMEText(body, 'plain'))

    # Attach the QR code image
    try:
        with open(qr_image_path, 'rb') as fp:
            img = MIMEImage(fp.read(), _subtype="png")
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(qr_image_path))
            msg.attach(img)
        print(f"QR code image attached: {qr_image_path}")
    except Exception as e:
        print(f"Failed to attach QR code image {qr_image_path}: {e}")


    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"QR code email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send QR code email to {recipient_email}: {e}")
        return False


# --- Main Script ---
if __name__ == "__main__":
    print("Starting daily QR code generation script with retries...")

    process_successful = False
    qr_image_filename = "daily_meal_qr.png" # Define filename outside the loop

    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1} of {MAX_RETRIES}...")

            qr_data_string, today_date, daily_token = generate_daily_qr_data()
            
            generated_image_path = generate_qr_code_image(qr_data_string, qr_image_filename)
            
            email_sent = send_qr_email(QR_RECIPIENT_EMAIL, generated_image_path, qr_data_string)
            
            if email_sent:
                process_successful = True
                print("Process completed successfully.")
                break

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if os.path.exists(qr_image_filename):
                 try:
                     os.remove(qr_image_filename)
                     print(f"Cleaned up temporary QR image file after failed attempt: {qr_image_filename}")
                 except Exception as cleanup_e:
                     print(f"Failed to clean up temporary QR image file after failed attempt: {cleanup_e}")


            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print("Maximum retries reached. Process failed.")
                
    if os.path.exists(qr_image_filename):
         try:
             os.remove(qr_image_filename)
             print(f"Final cleanup of temporary QR image file: {qr_image_filename}")
         except Exception as cleanup_e:
             print(f"Failed during final cleanup of temporary QR image file: {cleanup_e}")


    if not process_successful:
        print("Script finished with errors.")
        exit(1)

    print("Daily QR code script finished.")