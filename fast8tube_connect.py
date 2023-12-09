from googleapiclient.discovery import build

API_KEY = ''
CHANNEL_ID = 'UCY9653K77Aznsf9Q3kKrDQA'


def download_videos_list():

    service = build('youtube', 'v3', developerKey=API_KEY)
    r = service.channels().list(id=CHANNEL_ID, part='contentDetails').execute()
    uploads_id = r['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    args = {
        'playlistId': uploads_id,
        'part': 'snippet',
        'maxResults': 50
    }

    r = service.playlistItems().list(**args).execute()
    for item in r['items']:
        snpt = item['snippet']
        videos.append({
            'type': snpt['resourceId']['kind'],
            'videoId': snpt['resourceId'].get('videoId'),
            'publishedAt': snpt['publishedAt'],
            'title': snpt['title'],
        })