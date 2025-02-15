# Make CRON job to run this every minute and check if any users want to be notified this minute

from send_email import send_email
from datetime import datetime
import os
import psycopg2

connection = psycopg2.connect(database="users", user='postgres',
                              password=os.environ.get('POSTGRES_PASSWORD'), host="localhost", port=5432)
cursor = connection.cursor()

current_datetime = datetime.now()
current_time = current_datetime.time()

query = 'SELECT user_id, email FROM users WHERE notification_time=%s'

cursor.execute(query, (current_time.strftime('%H:%M'),))

# Fetch all rows from database
record = cursor.fetchall()
for user_id, email in record:
    send_email(user_id, email)
