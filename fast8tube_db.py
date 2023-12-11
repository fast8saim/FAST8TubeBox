import sqlite3 as sql


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
        cursor.execute(query, __parameters=parameters)
    connection.commit()

    if close:
        connection.close()


def query_select(query, connection, parameters=None):
    connection = db_connect()

    cursor = connection.cursor()
    if parameters is None:
        cursor.execute(query)
    else:
        cursor.execute(query, __parameters=parameters)

    return cursor.fetchall()


def check_db():
    connection = db_connect()
    query_insert(
        '''
        CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        API_KEY TEXT NOT NULL
        )
        ''', connection)
    query_insert(
        '''
        CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY,
        youtube_id TEXT NOT NULL,
        name TEXT NOT NULL,
        from_begin BOOLEAN,
        from_new BOOLEAN
        )
        ''', connection)
    query_insert(
        '''
        CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY,
        youtube_id TEXT NOT NULL,
        name TEXT NOT NULL,
        channel_id TEXT NOT NULL
        )
        ''', connection)
    query_insert(
        '''
        CREATE INDEX IF NOT EXISTS idx_channel ON videos (channel_id)
        ''', connection)

    connection.close()


def add_channel(channel_id, channel_name):
    query_insert('INSERT INTO channels (youtube_id, name) VALUES (?, ?)', None, (channel_id, channel_name))


def add_video(channel_id, video_id, name):
    query_insert('INSERT INTO videos (youtube_id, name, channel_id) VALUES (?, ?, ?)', None, (video_id, name, channel_id))


def get_channels():
    connection = db_connect()
    result = query_select('SELECT youtube_id, name FROM channels', connection)

    channels = []
    for sample in result:
        channels.append({
            'youtube_id': sample[0],
            'name': sample[1]
        })
    connection.close()

    return channels


def get_videos_list():
    connection = db_connect()
    result = query_select('SELECT youtube_id, name, channel_id FROM videos', connection)

    videos = []
    for sample in result:
        videos.append({
            'youtube_id': sample[0],
            'name': sample[1],
            'channel_id': sample[2]
        })
    connection.close()

    return videos


def save_api_key(api_key):
    connection = db_connect()
    query_insert('DELETE FROM settings', connection)
    query_insert('INSERT INTO settings (API_KEY) VALUES (?)', connection, (api_key,))

    connection.close()


def get_api_key():
    connection = db_connect()
    result = query_select('SELECT API_KEY FROM settings LIMIT 1', connection)

    api_key = ''
    for sample in result:
        api_key = sample[0]
        break

    connection.close()
    return api_key
