import fast8tube_sql
import fast8tube_connect

API_KEY = ''


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

    def __init__(self, channel_id):
        self.channel_id = channel_id

    def read(self):
        result = fast8tube_sql.read_channel(self.channel_id)
        for sample in result:
            self.fill(sample)

    def fill(self, sample):
        self.channel_id = sample[0]
        self.title = sample[1]
        self.description = sample[2]
        self.subscribers = sample[3]
        self.from_begin = sample[4]
        self.from_new = sample[5]
        self.need_translate = sample[6]
        self.add_date = sample[7]
        self.uploads_id = sample[8]

    def write(self):
        fast8tube_sql.update_channel(self)

    def download_info(self):
        fast8tube_connect.download_channel_info(API_KEY, self)


class Channels:
    list = []

    def get(self):
        result = fast8tube_sql.read_channel()
        for sample in result:
            channel = Channel(sample[0])
            channel.fill(sample)
            self.list.append(channel)


class Video:
    video_id = ''
    title = ''
    channel_id = ''


class Category:
    id = 0
    name = ''
