from googleapiclient.discovery import build


def download_channel_info(api_key, channel):
    service = build('youtube', 'v3', developerKey=api_key)
    r = service.channels().list(id=channel.channel_id, part='snippet,contentDetails,statistics').execute()
    item = r['items'][0]
    snippet = item['snippet']
    title = snippet['title']
    description = snippet['description']
    subscribers = item['statistics']['subscriberCount']
    uploads_id = item['contentDetails']['relatedPlaylists']['uploads']

    channel.title = title
    channel.description = description
    channel.subscribers = subscribers
    channel.uploads_id = uploads_id


def download_videos_list(api_key, channel):
    uploads_id = channel.uploads_id
    channel_id = channel.channel_id
    service = build('youtube', 'v3', developerKey=api_key)

    args = {
        'playlistId': uploads_id,
        'part': 'snippet',
        'maxResults': 50
    }

    r = service.playlistItems().list(**args).execute()

    data = []
    for item in r['items']:
        snippet = item['snippet']
        data.append({
            'channel_id': channel_id,
            'video_id': snippet['resourceId']['videoId'],
            'title': snippet['title'],
            'published_at': snippet['publishedAt']
        })
    return data
