import sqlite3

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
        api_key TEXT NOT NULL,
        theme BOOLEAN NOT NULL)'''
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
        title TEXT NOT NULL,
        published_at timestamp NOT NULL,
        duration TEXT NOT NULL,
        view_count INTEGER NOT NULL,
        like_count INTEGER NOT NULL,
        comment_count INTEGER NOT NULL)'''
    query.update()
    query.text = 'CREATE INDEX IF NOT EXISTS idx_channel ON videos (channel_id)'
    query.update()
    query.text = '''
        CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER NOT NULL PRIMARY KEY,
        title TEXT NOT NULL)'''
    query.update()
    query.text = '''
        CREATE TABLE IF NOT EXISTS channel_categories (
        channel_id TEXT NOT NULL,
        category_id INTEGER NOT NULL)'''
    query.update()

    query.close_connection()


def save_settings(api_key, theme):
    query = Query(text='DELETE FROM settings')
    query.update()
    query.text = 'INSERT INTO settings (api_key, theme) VALUES (?, ?)'
    query.parameters = (api_key, theme)
    query.update(True)


def read_settings():
    query = Query(text='SELECT api_key, theme FROM settings LIMIT 1')
    result = query.select(True)

    api_key = ''
    theme = True
    for sample in result:
        api_key = sample[0]
        theme = bool(sample[1])
        break

    return api_key, theme


def update_channel(channel):
    query = Query(text='SELECT channel_id FROM channels WHERE channel_id = ?', parameters=(channel.channel_id,))
    if len(query.select()) == 0:
        query.text = 'INSERT INTO channels (title, description, subscribers, from_begin, from_new, need_translate, add_date, uploads_id, channel_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    else:
        query.text = 'UPDATE channels SET title = ?, description = ?, subscribers = ?, from_begin = ?, from_new = ?, need_translate = ?, add_date = ?, uploads_id = ? WHERE channel_id = ?'

    query.parameters = (
        channel.title,
        channel.description,
        channel.subscribers,
        1 if channel.from_begin else 0,
        1 if channel.from_new else 0,
        1 if channel.need_translate else 0,
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
        condition = 'WHERE channel_id = ?'
        parameters = (channel_id,)

    query.text = f'SELECT channel_id, title, description, subscribers, from_begin, from_new, need_translate, add_date, uploads_id FROM channels {condition} ORDER BY title'
    query.parameters = parameters
    return query.select(True)


def read_channel_category(channel_id):
    query = Query()
    query.text = '''
    SELECT
        categories.category_id AS category_id,
        categories.title AS title,
        CASE
            WHEN channel_categories.category_id IS NULL THEN
                0
            ELSE
                1
        END AS use
        FROM categories
            LEFT JOIN channel_categories
            ON categories.category_id = channel_categories.category_id
            AND channel_categories.channel_id = ?'''

    query.parameters = (channel_id,)
    return query.select(True)


def update_channel_category(channel):
    query = Query(text='DELETE FROM channel_categories WHERE channel_id = ?', parameters=(channel.channel_id,))
    query.update()
    for category in channel.categories:
        values = channel.categories.get(category)
        if values['use']:
            query.text = 'INSERT INTO channel_categories (channel_id, category_id) VALUES (?, ?)'
            query.parameters = (channel.channel_id, category)
            query.update()

    query.close_connection()


def update_category(category):
    query = Query()
    if category.category_id == 0:
        query.text = 'INSERT INTO categories (title) VALUES (?)'
        query.parameters = (category.title,)
    else:
        query.text = 'UPDATE categories SET title = ? WHERE category_id = ?'
        query.parameters = (category.title, category.category_id)

    query.update(True)


def read_category(category_id=None):
    query = Query()

    if category_id is None:
        condition = ''
        parameters = ()
    else:
        condition = 'WHERE category_id = ?'
        parameters = (category_id,)

    query.text = f'SELECT category_id, title FROM categories {condition} ORDER BY title'
    query.parameters = parameters
    return query.select(True)


def update_video(video):
    query = Query(text='SELECT video_id FROM videos WHERE video_id = ?', parameters=(video.video_id,))
    if len(query.select()) == 0:
        query.text = 'INSERT INTO videos (title, channel_id, published_at, duration, view_count, like_count, comment_count, video_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    else:
        query.text = 'UPDATE videos SET title = ?, channel_id = ?, published_at = ?, duration = ?, view_count = ?, like_count = ?, comment_count = ? WHERE video_id = ?'

    query.parameters = (
        video.title,
        video.channel_id,
        video.published_at,
        video.duration,
        video.view_count,
        video.like_count,
        video.comment_count,
        video.video_id)
    query.update(True)


def read_video(video_id=None):
    query = Query()

    if video_id is None:
        condition = ''
        parameters = ()
    else:
        condition = 'WHERE video_id = ?'
        parameters = (video_id,)

    query.text = f'SELECT video_id, channel_id, title, published_at, duration, view_count, like_count, comment_count FROM videos {condition} ORDER BY published_at DESC LIMIT 100'
    query.parameters = parameters
    return query.select(True)
