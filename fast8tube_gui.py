import flet as ft
import fast8tube_db as f8db
import fast8tube_connect as f8con


def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"
    page.theme_mode = ft.ThemeMode.DARK

    def page_resize(e):
        print("New page size:", page.window_width, page.window_height)

    page.on_resize = page_resize

    api_key_field = ft.TextField(label='Ключ google-api', password=True, can_reveal_password=True)
    api_key_field.value = f8db.get_api_key()
    channel_id_field = ft.TextField(label='id канала')

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

    page.add(
        ft.Row([
            ft.FloatingActionButton(icon=ft.icons.SETTINGS, on_click=open_settings),
            ft.FloatingActionButton(icon=ft.icons.ADD, text='Добавить канал', on_click=open_channel_add)
        ])
    )

    channels_list = ft.ListView(width=400)
    videos_list = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True, width=500, height=page.height - 20)

    page.add(
        ft.Row([
            channels_list,
            videos_list
        ])
    )

    channels = f8db.get_channels()
    for channel in channels:
        channels_list.controls.append(
            ft.ListTile(
                title=ft.Text(channel.title),
                subtitle=ft.Text(channel.channel_id),
                leading=ft.Icon(ft.icons.ABC),
                trailing=ft.PopupMenuButton(
                    icon=ft.icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="Настроить", icon=ft.icons.MENU_OPEN),
                        ft.ElevatedButton(text="Обновить", icon=ft.icons.REFRESH, on_click=update_videos, data=channel.channel_id),
                        ft.PopupMenuItem(text="Удалить", icon=ft.icons.DELETE)
                    ]
                )
            )
        )

    videos = f8db.get_videos_list()

    for video in videos:
        videos_list.controls.append(ft.Text(video.title))

    page.update()


def create_gui():
    ft.app(target=main_window)
