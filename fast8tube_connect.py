from googleapiclient.discovery import build
import fast8tube_db as f8db


def download_videos_list(api_key, channel_id):

    service = build('youtube', 'v3', developerKey=api_key)
    r = service.channels().list(id=channel_id, part='contentDetails').execute()
    uploads_id = r['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    args = {
        'playlistId': uploads_id,
        'part': 'snippet',
        'maxResults': 50
    }

    r = service.playlistItems().list(**args).execute()
    for item in r['items']:
        snippet = item['snippet']
        f8db.add_video(channel_id, snippet['resourceId'].get('videoId'), snippet['title'])

        # 'type': snpt['resourceId']['kind'],
        # 'publishedAt': snpt['publishedAt'],
