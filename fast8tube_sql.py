import sqlite3 as sql
import fast8tube_data as f8data


class Query:
    text = ''


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
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        subscribers INTEGER NOT NULL,
        from_begin BOOLEAN NOT NULL,
        from_new BOOLEAN NOT NULL,
        need_translate BOOLEAN NOT NULL,
        add_date timestamp NOT NULL,
        uploads_id TEXT NOT NULL
        )
        ''', connection=connection)
    query_insert(
        query='''
        CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT NOT NULL PRIMARY KEY,
        channel_id TEXT NOT NULL,
        title TEXT,
        published_at timestamp NOT NULL
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


def update_channel(channel):
    connection = db_connect()
    result = query_select(query='SELECT channel_id WHERE channel_id = ?', connection=connection, parameters=(channel.channel_id,))
    if len(result) == 0:
        query = 'INSERT INTO channels (title, description, subscribers, from_begin, from_new, need_translate, add_date, uploads_id, channel_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    else:
        query = 'UPDATE channels SET title = ?, description = ?, subscribers = ?, from_begin = ?, from_new = ?, need_translate = ?, add_date = ?, uploads_id = ? WHERE channel_id = ?'

    query_insert(query=query, connection=connection, parameters=(channel.title, channel.description, channel.subscribers, channel.from_begin, channel.from_new, channel.need_translate, channel.add_date, channel.uploads_id, channel.channel_id))
    connection.close()


def get_channel(channel_id=None):
    connection = db_connect()
    query = 'SELECT channel_id, title, description, subscribers, from_begin, from_new, need_translate, add_date, uploads_id FROM channels ORDER BY title'
    if channel_id is None:
        parameters = None
    else:
        query = query + ' WHERE channel_id = ?'
        parameters = (channel_id,)

    result = query_select(query=query, connection=connection, parameters=parameters)
    connection.close()
    return result


def add_video(channel_id, video_id, name, published_at):
    query_insert(query='INSERT INTO videos (video_id, title, channel_id, published_at) VALUES (?, ?, ?, ?)', parameters=(video_id, name, channel_id, published_at))


def add_category(name):
    query_insert(query='INSERT INTO categories (name) VALUES (?)', parameters=(name,))


def get_categories():
    connection = db_connect()
    result = query_select(query='SELECT id, name FROM categories ORDER BY name', connection=connection)

    categories = []
    for sample in result:
        category = f8data.Category()
        category.id = sample[0]
        category.name = sample[1]
        categories.append(category)

    connection.close()

    return categories


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
