import flet as ft
import fast8tube_sql as f8db
import fast8tube_connect as f8con
import fast8tube_data as f8data
from fast8tube_data import Channels


def fill_videos(videos_list):
    videos = f8db.read_videos_list()
    for video in videos:
        videos_list.controls.append(ft.Text(video.title))


def fill_channels(channels_list, update_videos):
    channels = Channels()
    channels.get()

    for channel in channels.list:
        channels_list.controls.append(
            ft.ListTile(
                title=ft.Text(channel.title),
                subtitle=ft.Text(channel.channel_id),
                leading=ft.Icon(ft.icons.ABC),
                trailing=ft.PopupMenuButton(
                    icon=ft.icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="Настроить", icon=ft.icons.MENU_OPEN),
                        ft.PopupMenuItem(text="Обновить", icon=ft.icons.REFRESH, on_click=update_videos,
                                         data=channel.channel_id),
                        ft.PopupMenuItem(text="Удалить", icon=ft.icons.DELETE)
                    ]
                )
            )
        )


def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_title_bar_hidden = True

    f8db.check_database()
    f8data.API_KEY = f8db.read_api_key()

    api_key_field = ft.TextField(label='Ключ google-api', password=True, can_reveal_password=True)
    api_key_field.value = f8data.API_KEY
    channel_id_field = ft.TextField(label='id канала')

    def close_dialog_settings(e):
        dialog_settings.open = False
        page.update()

    def save_close_dialog_settings(e):
        f8db.save_api_key(api_key_field.value)
        close_dialog_settings(e)

    dialog_settings = ft.AlertDialog(
        modal=True,
        title=ft.Text('Настройки', width=400),
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
            channel = f8data.Channel(channel_id_field.value)
            channel.read()
            channel.download_info()
            channel.write()
        close_dialog_add_channel(e)

    dialog_add_channel = ft.AlertDialog(
        modal=True,
        title=ft.Text('Youtube-канал', width=400),
        content=ft.Column([
            channel_id_field,
            ft.Checkbox(label='Смотреть новое'),
            ft.Checkbox(label='Смотреть с начала')
        ]
        ),
        actions=[
            ft.TextButton("Сохранить", on_click=save_close_dialog_add_channel),
            ft.TextButton("Закрыть", on_click=close_dialog_add_channel)
        ]
    )

    def update_videos(e):
        channel_id = e.control.data
        if len(channel_id) > 3:
            f8con.download_videos_list(api_key_field.value, channel_id)

    def open_settings(e):
        page.dialog = dialog_settings
        dialog_settings.open = True
        page.update()

    def open_channel_add(e):
        page.dialog = dialog_add_channel
        dialog_add_channel.open = True
        page.update()

    main_column = ft.Column(expand=True, height=page.height)
    slide_column = ft.Column(expand=False, auto_scroll=False, width=400, height=page.height)
    page.add(
        ft.Row([
            main_column,
            slide_column
        ])
    )

    videos_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=False, height=page.height)
    main_column.controls.append(videos_list)

    slide_column.controls.append(
        ft.Row([
            ft.WindowDragArea(
                ft.Container(ft.Text("FAST8 Tube box"), bgcolor=ft.colors.GREEN_ACCENT_700, padding=10),
                expand=True),
            ft.IconButton(icon=ft.icons.SETTINGS, on_click=open_settings),
            ft.IconButton(ft.icons.CLOSE, on_click=lambda _: page.window_close())
        ])
    )
    slide_column.controls.append(
        ft.Tabs(
            selected_index=0,
            #on_change=tabs_changed,
            tabs=[ft.Tab(text="Каналы"), ft.Tab(text="Категории")]
        )
    )
    channels_list = ft.ListView(expand=False, spacing=5, padding=5, auto_scroll=False, width=400, height=page.height - 100)
    slide_column.controls.append(channels_list)

    fill_channels(channels_list, update_videos)
    fill_videos(videos_list)

    categories = f8db.read_categories()
    for category in categories:
        pass

    def page_resize(e):
        main_column.height = page.window_height
        slide_column.height = page.window_height
        videos_list.height = page.window_height
        page.update()

    page.on_resize = page_resize

    page.update()


def create_gui():
    ft.app(target=main_window)
