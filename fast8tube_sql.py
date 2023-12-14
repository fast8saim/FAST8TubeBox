import sqlite3
import fast8tube_data as f8data

DATABASE_NAME = 'fast8tubebox.db'


class Query:
    text = ''
    parameters = ()
    connection = None

    def __init__(self, text='', parameters=()):
        self.connection = sqlite3.connect(DATABASE_NAME)
        self.text = text
        self.parameters = parameters

    def __query(self):
        cursor = self.connection.cursor()
        cursor.execute(self.text, self.parameters)
        return cursor

    def update(self, close=False):
        self.__query()
        self.connection.commit()
        if close:
            self.close_connection()

    def select(self, close=False):
        cursor = self.__query()
        result = cursor.fetchall()
        if close:
            self.close_connection()
        return result

    def close_connection(self):
        if self.connection:
            self.connection.close()


def check_database():
    query = Query()
    query.text = '''
        CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        API_KEY TEXT NOT NULL)'''
    query.update()
    query.text = '''
        CREATE TABLE IF NOT EXISTS channels (
        channel_id TEXT NOT NULL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        subscribers INTEGER NOT NULL,
        from_begin BOOLEAN NOT NULL,
        from_new BOOLEAN NOT NULL,
        need_translate BOOLEAN NOT NULL,
        add_date timestamp NOT NULL,
        uploads_id TEXT NOT NULL)'''
    query.update()
    query.text = '''
        CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT NOT NULL PRIMARY KEY,
        channel_id TEXT NOT NULL,
        title TEXT,
        published_at timestamp NOT NULL)'''
    query.update()
    query.text = 'CREATE INDEX IF NOT EXISTS idx_channel ON videos (channel_id)'
    query.update()
    query.text = '''
        CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL)'''
    query.update()

    query.close_connection()


def save_api_key(api_key):
    query = Query(text='DELETE FROM settings')
    query.update()
    query.text = 'INSERT INTO settings (API_KEY) VALUES (?)'
    query.parameters = (api_key,)
    query.update(True)


def read_api_key():
    query = Query(text='SELECT API_KEY FROM settings LIMIT 1')
    result = query.select(True)

    api_key = ''
    for sample in result:
        api_key = sample[0]
        break

    return api_key


def update_channel(channel):
    query = Query(text='SELECT channel_id WHERE channel_id = ?', parameters=(channel.channel_id,))
    if len(query.select()) == 0:
        query.text = 'INSERT INTO channels (title, description, subscribers, from_begin, from_new, need_translate, add_date, uploads_id, channel_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    else:
        query.text = 'UPDATE channels SET title = ?, description = ?, subscribers = ?, from_begin = ?, from_new = ?, need_translate = ?, add_date = ?, uploads_id = ? WHERE channel_id = ?'

    query.parameters = (
        channel.title,
        channel.description,
        channel.subscribers,
        channel.from_begin,
        channel.from_new,
        channel.need_translate,
        channel.add_date,
        channel.uploads_id,
        channel.channel_id
    )
    query.update(True)


def read_channel(channel_id=None):
    query = Query()

    if channel_id is None:
        condition = ''
        parameters = ()
    else:
        condition = ' WHERE channel_id = ?'
        parameters = (channel_id,)

    query.text = f'SELECT channel_id, title, description, subscribers, from_begin, from_new, need_translate, add_date, uploads_id FROM channels ORDER BY title {condition}'
    query.parameters = parameters
    return query.select(True)


def add_video(channel_id, video_id, name, published_at):
    query = Query(text='INSERT INTO videos (video_id, title, channel_id, published_at) VALUES (?, ?, ?, ?)', parameters=(video_id, name, channel_id, published_at))
    query.update(True)


def add_category(name):
    query = Query(text='INSERT INTO categories (name) VALUES (?)', parameters=(name,))
    query.update(True)


def read_categories():
    query = Query(text='SELECT id, name FROM categories ORDER BY name')
    result = query.select(True)

    categories = []
    for sample in result:
        category = f8data.Category()
        category.id = sample[0]
        category.name = sample[1]
        categories.append(category)

    return categories


def read_videos_list():
    query = Query(text='SELECT video_id, title, channel_id FROM videos LIMIT 100')
    result = query.select()

    videos = []
    for sample in result:
        video = f8data.Video()
        video.video_id = sample[0]
        video.title = sample[1]
        video.channel_id = sample[2]

        videos.append(video)

    return videos
