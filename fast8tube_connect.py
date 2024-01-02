from googleapiclient.discovery import build
import datetime


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


def format_duration(duration):
    h = 0
    m = 0
    s = 0

    r = duration[2:]
    if 'H' in r:
        r = r.split('H')
        h = r[0]
        r = r[1]
    if 'M' in r:
        r = r.split('M')
        m = r[0]
        r = r[1]
    if 'S' in r:
        r = r.split('S')
        s = r[0]

    return f'{h}:{m}:{s}'


def download_videos_list(api_key, channel):
    uploads_id = channel.uploads_id
    channel_id = channel.channel_id
    service = build('youtube', 'v3', developerKey=api_key)

    args = {
        'playlistId': uploads_id,
        'part': 'snippet',
        'maxResults': 50
    }

    data = []
    for _ in range(0, 500):
        video_ids = []
        r = service.playlistItems().list(**args).execute()
        for item in r['items']:
            snippet = item['snippet']
            video_ids.append(snippet['resourceId']['videoId'])

        args['pageToken'] = r.get('nextPageToken')

        r = service.videos().list(id=video_ids, part='snippet,contentDetails,statistics').execute()
        for item in r['items']:
            data.append({
                'channel_id': channel_id,
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'published_at': datetime.datetime.strptime(item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                'duration': format_duration(item['contentDetails']['duration']),
                'view_count': item['statistics']['viewCount'],
                'like_count': item['statistics']['likeCount'],
                'comment_count': item['statistics']['commentCount'],
                'thumb_address': item['snippet']['thumbnails']['medium']['url']
            })

        if not args['pageToken']:
            break

    return data
