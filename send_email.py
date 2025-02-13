import smtplib
from email.mime.text import MIMEText
import requests
import json
import os


subject = "Automated Notifications"
sender = os.environ.get('NOTIFICATION_EMAIL')
password = os.environ.get('EMAIL_PASSWORD')


def get_new_youtube_uploads(user_id):
    url = 'http://127.0.0.1:8000/videos/' + str(user_id)
    response = requests.get(url)
    print(response.text)
    vids = json.loads(response.text)
    return vids


def send_email(user_id, email):
    vids = get_new_youtube_uploads(user_id)
    body = ''
    for vid in vids:
        body += 'Channel: ' + vid['channel'] + '\n'
        body += 'Title: ' + vid['title'] + '\n'
        body += 'URL: ' + 'https://www.youtube.com/watch?v=' + str(vid['video_id']) + '\n'
        body += '\n'
    if body:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, [email], msg.as_string())
            print("Message sent!")
