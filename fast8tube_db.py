import sqlite3 as sql
import fast8tube_data as f8data


def db_connect():
    return sql.connect('fast8tubebox.db')


def query_insert(query, connection=None, parameters=None):
    close = False
    if connection is None:
        connection = db_connect()
        close = True

    cursor = connection.cursor()
    if parameters is None:
        cursor.execute(query)
    else:
        cursor.execute(query, parameters)
    connection.commit()

    if close:
        connection.close()


def query_select(query, connection, parameters=None):
    cursor = connection.cursor()
    if parameters is None:
        cursor.execute(query)
    else:
        cursor.execute(query, parameters)

    return cursor.fetchall()


def check_db():
    connection = db_connect()
    query_insert(
        query='''
        CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        API_KEY TEXT NOT NULL
        )
        ''', connection=connection)
    query_insert(
        query='''
        CREATE TABLE IF NOT EXISTS channels (
        channel_id TEXT NOT NULL PRIMARY KEY,
        title TEXT,
        description TEXT,
        subscribers INTEGER,
        from_begin BOOLEAN,
        from_new BOOLEAN
        )
        ''', connection=connection)
    query_insert(
        query='''
        CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT NOT NULL PRIMARY KEY,
        channel_id TEXT NOT NULL,
        title TEXT
        )
        ''', connection=connection)
    query_insert(
        query='''
        CREATE INDEX IF NOT EXISTS idx_channel ON videos (channel_id)
        ''', connection=connection)
    query_insert(
        query='''
            CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
            )
            ''', connection=connection)

    connection.close()


def add_channel(channel_id, channel_name):
    query_insert(query='INSERT INTO channels (channel_id, title) VALUES (?, ?)', parameters=(channel_id, channel_name))


def add_video(channel_id, video_id, name):
    query_insert(query='INSERT INTO videos (video_id, title, channel_id) VALUES (?, ?, ?)', parameters=(video_id, name, channel_id))


def add_category(name):
    query_insert(query='INSERT INTO categories (name) VALUES (?)', parameters=(name,))


def get_categories():
    connection = db_connect()
    result = query_select(query='SELECT name FROM categories', connection=connection)

    categories = []
    for sample in result:
        category = f8data.Category()
        category.name = sample[0]
        categories.append(category)

    connection.close()

    return categories


def update_channel_info(channel_id, title, description, subscribers):
    query_insert(query='UPDATE channels SET title = ?, description = ?, subscribers = ? WHERE channel_id = ?', parameters=(title, description, subscribers, channel_id))


def get_channels():
    connection = db_connect()
    result = query_select(query='SELECT channel_id, title FROM channels', connection=connection)

    channels = []
    for sample in result:
        channel = f8data.Channel()
        channel.channel_id = sample[0]
        channel.title = sample[1]
        channels.append(channel)

    connection.close()

    return channels


def get_videos_list():
    connection = db_connect()
    result = query_select(query='SELECT video_id, title, channel_id FROM videos LIMIT 100', connection=connection)

    videos = []
    for sample in result:
        video = f8data.Video()
        video.video_id = sample[0]
        video.title = sample[1]
        video.channel_id = sample[2]

        videos.append(video)
    connection.close()

    return videos


def save_api_key(api_key):
    connection = db_connect()
    query_insert(query='DELETE FROM settings', connection=connection)
    query_insert(query='INSERT INTO settings (API_KEY) VALUES (?)', connection=connection, parameters=(api_key,))

    connection.close()


def get_api_key():
    connection = db_connect()
    result = query_select(query='SELECT API_KEY FROM settings LIMIT 1', connection=connection)

    api_key = ''
    for sample in result:
        api_key = sample[0]
        break

    connection.close()
    return api_key
