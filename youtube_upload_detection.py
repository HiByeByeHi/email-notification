import os
import fastapi
import googleapiclient.discovery
import psycopg2
from datetime import datetime, timedelta
import html


api_service_name = 'youtube'
api_version = 'v3'
youtube = googleapiclient.discovery.build(api_service_name, api_version,
    developerKey = os.environ.get('YOUTUBE_API_KEY'))

connection = psycopg2.connect(database="youtube", user='postgres',
                              password=os.environ.get('POSTGRES_PASSWORD'), host="localhost", port=5432)
connection.autocommit = True
cursor = connection.cursor()

app = fastapi.FastAPI()


@app.get('/channel/{handle}')
def get_channel_id(handle):
    request = youtube.channels().list(part='snippet', forHandle=handle)
    response = request.execute()
    return response['items'][0]['id']


def get_videos(channel_id, start_date):
    request = youtube.search().list(part='snippet', channelId=channel_id, type='video', order='date',
                                    publishedAfter=start_date)
    response = request.execute()
    res = []
    while response:
        print(response)
        for i in range(int(response['pageInfo']['resultsPerPage'])):
            res.append(({'channel': response['items'][i]['snippet']['channelTitle'],
                         'publication_date': response['items'][i]['snippet']['publishedAt'],
                         'title': html.unescape(response['items'][i]['snippet']['title']),
                         'video_id': response['items'][i]['id']['videoId'],
                         'thumbnail': response['items'][i]['snippet']['thumbnails']['default']['url']}))
        if 'nextPageToken' in response:
            request = youtube.search().list(part='snippet', channelId=channel_id, type='video',
                                            order='date', publishedAfter=start_date,
                                            pageToken=response['nextPageToken'])
            response = request.execute()
        else:
            response = None
    print(res)
    return res


def retrieve_last_pulls(user_id):
    sql_context = 'SELECT channel, last_pull FROM last_pull WHERE user_id=%s'

    cursor.execute(sql_context, (user_id,))

    # Fetch all rows from database
    record = cursor.fetchall()

    print("Data from Database:- ", record)
    return record


@app.get('/videos/{user_id}')
def process_job(user_id):
    channels = retrieve_last_pulls(user_id)
    res = []
    for channel, timestamp in channels:
        new_vids = get_videos(channel, timestamp)
        if new_vids:
            date = (datetime.strptime(new_vids[0]['publication_date'], '%Y-%m-%dT%H:%M:%SZ') +
                    timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            query = 'UPDATE last_pull SET last_pull=%s WHERE channel=%s AND user_id=%s'
            cursor.execute(query, (date, channel, user_id))
        res += new_vids
    return res
