import flet as ft
import fast8tube_sql
import fast8tube_data
from fast8tube_data import Channel, Channels, Categories, Videos


class ChannelForm(ft.UserControl):
    page = None
    channel = None
    categories_list = None
    checkbox_from_new = None
    checkbox_from_begin = None
    checkbox_need_translate = None

    def close_dialog_edit_channel(self, e):
        self.controls.open = False
        self.page.update()

    def save_close_dialog_edit_channel(self, e):
        for i in self.categories_list.controls:
            checkbox = i.controls[0]
            self.channel.categories[checkbox.data['id']]['use'] = checkbox.value

        self.channel.from_new = self.checkbox_from_new.value
        self.channel.from_begin = self.checkbox_from_begin.value
        self.channel.need_translate = self.checkbox_need_translate.value

        self.channel.write()
        self.channel.write_categories()
        self.close_dialog_edit_channel(e)

    def __init__(self, page: ft.Page, channel: Channel):
        super().__init__()
        self.page = page
        self.channel = channel
        self.controls = self.build()
        self.page.update()

    def build(self):
        channel_id_field = ft.TextField(label='id канала', width=500)
        channel_id_field.value = self.channel.channel_id
        if channel_id_field.value:
            channel_id_field.disabled = True
        self.channel.read()
        self.categories_list = ft.ListView(expand=False, spacing=5, padding=5, auto_scroll=False, width=400, height=self.page.height)
        for category in self.channel.categories:
            values = self.channel.categories.get(category)
            self.categories_list.controls.append(
                ft.Row([
                    ft.Checkbox(label=values['title'], value=values['use'], data={'id': category, 'title': values['title'], 'use': values['use']})
                ])
            )

        self.checkbox_from_new = ft.Checkbox(label='Смотреть новое', value=self.channel.from_new, width=500)
        self.checkbox_from_begin = ft.Checkbox(label='Смотреть с начала', value=self.channel.from_begin, width=500)
        self.checkbox_need_translate = ft.Checkbox(label='Нужен перевод', value=self.channel.need_translate, width=500)

        edit_channel_content = ft.Row(
            [
                ft.Column([
                    channel_id_field,
                    ft.TextField(label='Заголовок', disabled=True, value=self.channel.title, width=500),
                    ft.TextField(label='Описание', disabled=True, value=self.channel.description, width=500),
                    ft.TextField(label='Подписчиков', disabled=True, value=self.channel.subscribers, width=500),
                    ft.TextField(label='Дата добавления', disabled=True, value=self.channel.add_date, width=500),
                    ft.TextField(label='uploads_id', disabled=True, value=self.channel.uploads_id, width=500),
                    self.checkbox_from_new,
                    self.checkbox_from_begin,
                    self.checkbox_need_translate]),
                self.categories_list
            ], width=800)

        dialog_edit_channel = dialog('Youtube-канал', edit_channel_content, [
            ft.TextButton("Сохранить", on_click=self.save_close_dialog_edit_channel),
            ft.TextButton("Закрыть", on_click=self.close_dialog_edit_channel)])
        self.page.dialog = dialog_edit_channel
        dialog_edit_channel.open = True

        return dialog_edit_channel


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

    api_key_field = ft.TextField(label='Ключ google-api', password=True, can_reveal_password=True)
    api_key_field.value = fast8tube_data.API_KEY

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

    channels_list = ft.ListView(expand=False, spacing=5, padding=5, auto_scroll=False, width=400,
                                height=page.height - 100)
    categories_list = ft.ListView(expand=False, spacing=5, padding=5, auto_scroll=False, width=400,
                                  height=page.height - 100)

    def update_videos(e):
        channel = e.control.data
        channel.download_info()
        channel.write()
        channel.download_videos_list()

    def open_settings(e):
        page.dialog = dialog_settings
        dialog_settings.open = True
        page.update()

    def edit_channel(e):
        ChannelForm(page, e.control.data)

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
