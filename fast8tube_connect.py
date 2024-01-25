from googleapiclient.discovery import build
from pytube import YouTube, Channel
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

    return f'{h}:{str(m).zfill(2)}:{str(s).zfill(2)}'


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
                'time': format_duration(item['contentDetails']['duration']),
                'view_count': item['statistics']['viewCount'] if 'viewCount' in item['statistics'] else 0,
                'like_count': item['statistics']['likeCount'] if 'likeCount' in item['statistics'] else 0,
                'comment_count': item['statistics']['commentCount'] if 'commentCount' in item['statistics'] else 0,
                'thumb_address': item['snippet']['thumbnails']['medium']['url']
            })

        if not args['pageToken']:
            break

    return data


def download_video_content(video, filepath):
    yt = YouTube(f'https://www.youtube.com/watch?v={video.video_id}')
    yt.streams.get_highest_resolution().download(output_path=filepath, filename=f'{video.video_id}.mp4')


def get_channel_id_by_url(api_key, url):
    service = build('youtube', 'v3', developerKey=api_key)
    channel_pos = url.find('&ab_channel=')
    if channel_pos != -1:
        url = url[:channel_pos]
    video_id = url.replace('https://', '').replace('www.youtube.com/', '').replace('watch?v=', '').replace('youtu.be/', '').replace('?feature=shared', '')
    r = service.videos().list(id=video_id, part='snippet').execute()
    channel_id = ''
    for item in r['items']:
        channel_id = item['snippet']['channelId']
        break

    return channel_id
