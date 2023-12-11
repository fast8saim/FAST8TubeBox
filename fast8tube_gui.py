import flet as ft
import fast8tube_db as f8db
import fast8tube_connect as f8con


def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"
    page.theme_mode = ft.ThemeMode.DARK

    api_key_field = ft.TextField(label='Ключ google-api', password=True, can_reveal_password=True)
    channel_id_field = ft.TextField(label='id канала')
    api_key_field.value = f8db.get_api_key()

    def close_dialog_settings(e):
        dialog_settings.open = False
        page.update()

    def save_close_dialog_settings(e):
        f8db.save_api_key(api_key_field.value)
        close_dialog_settings(e)

    dialog_settings = ft.AlertDialog(
        modal=True,
        title=ft.Text('Настройки'),
        content=api_key_field,
        actions=[
            ft.TextButton("Сохранить", on_click=save_close_dialog_settings),
            ft.TextButton("Закрыть", on_click=close_dialog_settings)
        ]
    )

    def close_dialog_add_channel(e):
        dialog_add_channel.open = False
        page.update()

    def save_close_dialog_add_channel(e):
        if len(channel_id_field.value) > 1:
            f8db.add_channel(channel_id_field.value, channel_id_field.value)
        close_dialog_add_channel(e)

    dialog_add_channel = ft.AlertDialog(
        modal=True,
        title=ft.Text('Добавить канал'),
        content=channel_id_field,
        actions=[
            ft.TextButton("Сохранить", on_click=save_close_dialog_add_channel),
            ft.TextButton("Закрыть", on_click=close_dialog_add_channel)
        ]
    )

    def update_videos(e):
        channel_id = 'UCY9653K77Aznsf9Q3kKrDQA'
        f8con.download_videos_list(api_key_field.value, channel_id)

    def open_settings(e):
        page.dialog = dialog_settings
        dialog_settings.open = True
        page.update()

    def open_channel_add(e):
        page.dialog = dialog_add_channel
        dialog_add_channel.open = True
        page.update()

    page.add(
        ft.Row([
            ft.FloatingActionButton(icon=ft.icons.SETTINGS, on_click=open_settings),
            ft.FloatingActionButton(icon=ft.icons.ADD, text='add channel', on_click=open_channel_add),
            ft.FloatingActionButton(icon=ft.icons.UPLOAD, text='update videos', on_click=update_videos)
        ])
    )

    channels_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text('id')),
            ft.DataColumn(ft.Text('name'))
        ]
    )
    videos_column = ft.Column(
        auto_scroll=False,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=1
    )

    channels = f8db.get_channels()
    page.add(
        ft.Row([
            channels_table,
            videos_column
        ])
    )

    for channel in channels:
        channels_table.rows.append(
            ft.DataRow([
                ft.DataCell(ft.Text(channel['youtube_id'])),
                ft.DataCell(ft.Text(channel['name']))
            ]),
            )

    videos = f8db.get_videos_list()

    for video in videos:
        videos_column.controls.append(ft.Text(video['name']))

    page.update()


def create_gui():
    ft.app(target=main_window)
