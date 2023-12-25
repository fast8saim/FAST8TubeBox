import fast8tube_sql
import fast8tube_connect
import datetime

API_KEY, THEME = fast8tube_sql.read_settings()


class Channel:
    channel_id = ''
    title = ''
    description = ''
    subscribers = 0
    from_begin = False
    from_new = False
    need_translate = False
    add_date = ''
    uploads_id = ''
    categories = {}

    def __init__(self, channel_id):
        self.channel_id = channel_id

    def read(self):
        result = fast8tube_sql.read_channel(self.channel_id)
        for sample in result:
            self.fill(sample)
        self.categories.clear()
        result = fast8tube_sql.read_channel_category(self.channel_id)
        for sample in result:
            if sample[2] == 1:
                use = True
            else:
                use = False
            self.categories.setdefault(sample[0], {'title': sample[1], 'use': use})

    def fill(self, sample):
        self.channel_id = sample[0]
        self.title = sample[1]
        self.description = sample[2]
        self.subscribers = sample[3]
        self.from_begin = True if sample[4] == 1 else False
        self.from_new = True if sample[5] == 1 else False
        self.need_translate = True if sample[6] == 1 else False
        self.add_date = sample[7]
        self.uploads_id = sample[8]

    def write(self):
        if not self.add_date:
            self.add_date = datetime.datetime.now()
        fast8tube_sql.update_channel(self)

    def write_categories(self):
        fast8tube_sql.update_channel_category(self)

    def download_info(self):
        fast8tube_connect.download_channel_info(API_KEY, self)

    def download_videos_list(self):
        data = fast8tube_connect.download_videos_list(API_KEY, self)
        for sample in data:
            video = Video(sample['video_id'])
            video.read()
            video.fill((
                sample['video_id'],
                sample['channel_id'],
                sample['title'],
                sample['published_at'],
                sample['duration'],
                sample['view_count'],
                sample['like_count'],
                sample['comment_count']))
            video.write()


class Channels:
    list = []

    def read(self):
        result = fast8tube_sql.read_channel()
        for sample in result:
            channel = Channel(sample[0])
            channel.fill(sample)
            self.list.append(channel)


class Category:
    category_id = 0
    title = ''

    def __init__(self, category_id=0, title=''):
        self.category_id = category_id
        self.title = title

    def read(self):
        result = fast8tube_sql.read_category(self.category_id)
        for sample in result:
            self.fill(sample)

    def fill(self, sample):
        self.category_id = sample[0]
        self.title = sample[1]

    def write(self):
        fast8tube_sql.update_category(self)


class Categories:
    list = []

    def read(self):
        result = fast8tube_sql.read_category()
        for sample in result:
            category = Category(sample[0])
            category.fill(sample)
            self.list.append(category)


class Video:
    video_id = ''
    title = ''
    channel_id = ''
    published_at = ''
    duration = ''
    view_count = 0
    like_count = 0
    comment_count = 0

    def __init__(self, video_id=''):
        self.video_id = video_id

    def read(self):
        result = fast8tube_sql.read_video(self.video_id)
        for sample in result:
            self.fill(sample)

    def fill(self, sample):
        self.video_id = sample[0]
        self.channel_id = sample[1]
        self.title = sample[2]
        self.published_at = sample[3]
        self.duration = sample[4]
        self.view_count = sample[5]
        self.like_count = sample[6]
        self.comment_count = sample[7]

    def write(self):
        fast8tube_sql.update_video(self)


class Videos:
    list = []

    def read(self):
        result = fast8tube_sql.read_video()
        for sample in result:
            video = Video(sample[0])
            video.fill(sample)
            self.list.append(video)
