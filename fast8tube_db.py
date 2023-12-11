import sqlite3 as sql


def check_db():
    connection = sql.connect('fast8tubebox.db')
    query = connection.cursor()

    query.execute(
        '''
        CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        API_KEY TEXT NOT NULL
        )
        '''
    )
    connection.commit()
    query.execute(
        '''
        CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY,
        youtube_id TEXT NOT NULL,
        name TEXT NOT NULL,
        from_begin BOOLEAN,
        from_new BOOLEAN
        )
        '''
    )
    connection.commit()
    query.execute(
        '''
        CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY,
        youtube_id TEXT NOT NULL,
        name TEXT NOT NULL,
        channel_id TEXT NOT NULL
        )
        '''
    )
    connection.commit()
    query.execute(
        '''
        CREATE INDEX IF NOT EXISTS idx_channel ON videos (channel_id)
        '''
    )
    connection.commit()

    connection.close()


def add_channel(channel_id, channel_name):
    connection = sql.connect('fast8tubebox.db')
    query = connection.cursor()
    query.execute('INSERT INTO channels (youtube_id, name) VALUES (?, ?)', (channel_id, channel_name))

    connection.commit()
    connection.close()


def add_video(channel_id, video_id, name):
    connection = sql.connect('fast8tubebox.db')
    query = connection.cursor()
    query.execute('INSERT INTO videos (youtube_id, name, channel_id) VALUES (?, ?, ?)', (video_id, name, channel_id))

    connection.commit()
    connection.close()


def get_channels():
    connection = sql.connect('fast8tubebox.db')
    query = connection.cursor()
    query.execute('SELECT youtube_id, name FROM channels')
    result = query.fetchall()

    channels = []
    for sample in result:
        channels.append({
            'youtube_id': sample[0],
            'name': sample[1]
        })
    connection.close()

    return channels


def get_videos_list():
    connection = sql.connect('fast8tubebox.db')
    query = connection.cursor()
    query.execute('SELECT youtube_id, name, channel_id FROM videos')
    result = query.fetchall()

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
    connection = sql.connect('fast8tubebox.db')
    query = connection.cursor()
    query.execute('DELETE FROM settings')
    query.execute('INSERT INTO settings (API_KEY) VALUES (?)', (api_key,))
    connection.commit()
    connection.close()


def get_api_key():
    connection = sql.connect('fast8tubebox.db')
    query = connection.cursor()
    query.execute('SELECT API_KEY FROM settings LIMIT 1')
    result = query.fetchall()
    api_key = ''
    for sample in result:
        api_key = sample[0]
        break

    connection.close()
    return api_key
