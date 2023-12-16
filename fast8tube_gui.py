import flet as ft
import fast8tube_sql
import fast8tube_data
from fast8tube_data import Channel, Channels, Categories, Videos


def fill_videos(videos_list):
    videos = Videos()
    videos.read()
    for video in videos.list:
        videos_list.controls.append(ft.Text(video.title))


def fill_channels(channels_list, update_videos, edit_channel):
    channels = Channels()
    channels.read()

    for channel in channels.list:
        channels_list.controls.append(
            ft.ListTile(
                title=ft.Text(channel.title),
                subtitle=ft.Text(channel.channel_id),
                leading=ft.Icon(ft.icons.ABC),
                trailing=ft.PopupMenuButton(
                    icon=ft.icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="Настроить", icon=ft.icons.MENU_OPEN, on_click=edit_channel,
                                         data=channel),
                        ft.PopupMenuItem(text="Обновить", icon=ft.icons.REFRESH, on_click=update_videos, data=channel),
                        ft.PopupMenuItem(text="Удалить", icon=ft.icons.DELETE, data=channel)
                    ]
                )
            )
        )


def fill_categories(categories_list):
    categories = Categories()
    categories.read()
    for category in categories.list:
        categories_list.controls.append(
                ft.ListTile(
                    title=ft.Text(category.title),
                    leading=ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET_SHARP)
                    )
                )


def dialog(title, content, actions):
    return ft.AlertDialog(
        modal=True,
        title=ft.Text(title, width=400),
        content=content,
        actions=actions)


def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"
    page.window_title_bar_hidden = True

    fast8tube_sql.check_database()
    page.theme_mode = ft.ThemeMode.DARK if fast8tube_data.THEME else ft.ThemeMode.LIGHT

    def change_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    current_channel = None

    api_key_field = ft.TextField(label='Ключ google-api', password=True, can_reveal_password=True)
    api_key_field.value = fast8tube_data.API_KEY

    channel_id_field = ft.TextField(label='id канала')

    def close_dialog_settings(e):
        dialog_settings.open = False
        page.update()

    def save_close_dialog_settings(e):
        fast8tube_sql.save_settings(api_key_field.value, page.theme_mode == ft.ThemeMode.DARK)
        close_dialog_settings(e)

    dialog_settings = dialog('Настройки', api_key_field, [
        ft.IconButton(icon=ft.icons.SUNNY, on_click=change_theme),
        ft.TextButton("Сохранить", on_click=save_close_dialog_settings),
        ft.TextButton("Закрыть", on_click=close_dialog_settings)])

    def close_dialog_edit_channel(e):
        dialog_edit_channel.open = False
        page.update()

    def save_close_dialog_edit_channel(e):
        current_channel.write()
        close_dialog_edit_channel(e)

    edit_channel_content = ft.Column([
        channel_id_field,
        ft.Checkbox(label='Смотреть новое'),
        ft.Checkbox(label='Смотреть с начала')])

    dialog_edit_channel = dialog('Youtube-канал', edit_channel_content, [
        ft.TextButton("Сохранить", on_click=save_close_dialog_edit_channel),
        ft.TextButton("Закрыть", on_click=close_dialog_edit_channel)])

    def update_videos(e):
        current_channel = e.control.data
        current_channel.download_videos_list()

    def open_settings(e):
        page.dialog = dialog_settings
        dialog_settings.open = True
        page.update()

    def edit_channel(e):
        current_channel = e.control.data
        current_channel.read()
        current_channel.download_info()
        channel_id_field.value = current_channel.channel_id
        page.dialog = dialog_edit_channel
        dialog_edit_channel.open = True
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

    def tabs_changed(e):
        if e.control.selected_index == 0:
            slide_column.controls.append(channels_list)
            slide_column.controls.remove(categories_list)
        else:
            slide_column.controls.remove(channels_list)
            slide_column.controls.append(categories_list)
        page.update()

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
            on_change=tabs_changed,
            tabs=[ft.Tab(text="Каналы"), ft.Tab(text="Категории")]
        )
    )
    channels_list = ft.ListView(expand=False, spacing=5, padding=5, auto_scroll=False, width=400,
                                height=page.height - 100)
    categories_list = ft.ListView(expand=False, spacing=5, padding=5, auto_scroll=False, width=400,
                                  height=page.height - 100)
    slide_column.controls.append(channels_list)

    fill_channels(channels_list, update_videos, edit_channel)
    fill_categories(categories_list)
    fill_videos(videos_list)

    def page_resize(e):
        main_column.height = page.window_height
        slide_column.height = page.window_height
        videos_list.height = page.window_height
        page.update()

    page.on_resize = page_resize

    page.update()


def create_gui():
    ft.app(target=main_window)
