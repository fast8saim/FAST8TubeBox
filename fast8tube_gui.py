import flet as ft
import fast8tube_sql
import fast8tube_data
from fast8tube_data import Channel, Channels, Category, Categories, Videos


class ChannelForm(ft.UserControl):
    new = True
    page = None
    channel = None
    categories_list = None
    checkbox_from_new = None
    checkbox_from_begin = None
    checkbox_need_translate = None
    channels_list = None

    def close_dialog_edit_channel(self, e):
        self.controls.open = False
        self.page.update()

    def save_close_dialog_edit_channel(self, e):
        self.channel.from_new = self.checkbox_from_new.value
        self.channel.from_begin = self.checkbox_from_begin.value
        self.channel.need_translate = self.checkbox_need_translate.value

        if self.new:
            self.channel.download_info()

        self.channel.write()
        self.channel.write_categories()

        self.channels_list.fill()
        self.close_dialog_edit_channel(e)

    def mark_category(self, e):
        self.channel.categories[e.control.data]['use'] = e.control.value

    def fill_channel_id(self, e):
        self.channel.channel_id = e.control.value

    def __init__(self, page: ft.Page, channel: Channel, channels_list):
        super().__init__()
        self.page = page
        self.channel = channel
        self.channels_list = channels_list
        self.controls = self.build()
        for category in self.channel.categories:
            values = self.channel.categories.get(category)
            self.categories_list.controls.append(ft.Row(
                [ft.Checkbox(label=values['title'], value=values['use'], data=category, on_change=self.mark_category)]))
        self.page.update()

    def build(self):
        channel_id_field = ft.TextField(label='id канала', width=500, on_change=self.fill_channel_id)
        channel_id_field.value = self.channel.channel_id
        if channel_id_field.value:
            self.new = False
            channel_id_field.disabled = True
            self.channel.read()

        self.categories_list = ft.ListView(expand=True, spacing=5, padding=5, auto_scroll=False, width=400,
                                           height=self.page.height)
        self.checkbox_from_new = ft.Checkbox(label='Смотреть новое', value=self.channel.from_new, width=500)
        self.checkbox_from_begin = ft.Checkbox(label='Смотреть с начала', value=self.channel.from_begin, width=500)
        self.checkbox_need_translate = ft.Checkbox(label='Нужен перевод', value=self.channel.need_translate, width=500)

        edit_channel_content = ft.Row(
            [
                ft.Column([
                    channel_id_field,
                    ft.Text(expand=True, value=self.channel.description, width=500),
                    ft.TextField(label='Подписчиков', disabled=True, value=self.channel.subscribers, width=500),
                    ft.TextField(label='Дата добавления', disabled=True, value=self.channel.add_date, width=500),
                    self.checkbox_from_new,
                    self.checkbox_from_begin,
                    self.checkbox_need_translate]),
                ft.Column([ft.Text(value='Категории:'), self.categories_list])
            ], width=800)

        dialog_edit_channel = dialog(f'Youtube-канал {self.channel.title}', edit_channel_content, [
            ft.TextButton("Сохранить", on_click=self.save_close_dialog_edit_channel),
            ft.TextButton("Закрыть", on_click=self.close_dialog_edit_channel)])
        self.page.overlay.append(dialog_edit_channel)
        dialog_edit_channel.open = True

        return dialog_edit_channel


class VideosList(ft.UserControl):
    page = None

    def mark_view(self, e):
        video = e.control.data
        video.mark_view()
        self.fill()
        self.page.update()

    def mark_skip(self, e):
        video = e.control.data
        video.mark_skip()
        self.fill()
        self.page.update()

    def download(self, e):
        video = e.control.data
        video.download_thumb()
        self.fill()
        self.page.update()

    def fill(self):
        self.controls.controls.clear()

        videos = Videos()
        videos.read()
        for video in videos.list:
            self.controls.controls.append(
                ft.Row([
                    ft.Image(src_base64=video.thumb_data, width=320),
                    ft.Column([
                        ft.Text(video.title),
                        ft.Text(f'{video.channel.title} {video.channel.categories_title}'),
                        ft.Text(f'длительность {video.time} дата {video.published_at.strftime("%Y.%m.%d")} просмотров {video.view_count} лайков {video.like_count} комментариев {video.comment_count}'),
                        ft.Row([
                            ft.TextButton(text="Загрузить", icon=ft.icons.DOWNLOAD, data=video, on_click=self.download),
                            ft.TextButton(text="Посмотреть", icon=ft.icons.MENU_OPEN, data=video, on_click=self.mark_view),
                            ft.TextButton(text="Пропустить", icon=ft.icons.REFRESH, data=video, on_click=self.mark_skip)])])]))

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.controls = self.build()

    def build(self):
        return ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=False, height=self.page.height)


class ChannelsList(ft.UserControl):
    page = None
    channels_list = None
    videos_list = None

    def add_channel(self, e):
        ChannelForm(self.page, Channel(''), self)

    def edit_channel(self, e):
        ChannelForm(self.page, e.control.data, self)

    def update_videos(self, e):
        channel = e.control.data
        channel.download_info()
        channel.write()
        channel.download_videos_list()
        self.videos_list.fill()
        self.page.update()

    def fill(self):
        self.channels_list.controls.clear()

        channels = Channels()
        channels.read()

        for channel in channels.list:
            self.channels_list.controls.append(
                ft.Row([ft.Text(channel.title), ft.Text(channel.categories_title),
                        ft.TextButton(text="Настроить", icon=ft.icons.MENU_OPEN, on_click=self.edit_channel,
                                         data=channel),
                        ft.TextButton(text="Обновить", icon=ft.icons.REFRESH, on_click=self.update_videos,
                                         data=channel),
                        ft.TextButton(text="Удалить", icon=ft.icons.DELETE, data=channel)]))

    def __init__(self, page: ft.Page, videos_list):
        super().__init__()
        self.page = page
        self.videos_list = videos_list
        self.controls = self.build()

    def build(self):
        self.channels_list = ft.ListView(expand=True, spacing=5, padding=5, auto_scroll=False, width=400, height=self.page.height - 200)
        channels_column = ft.Column([
            ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_channel),
            self.channels_list])
        return channels_column


class CategoriesList(ft.UserControl):
    page = None

    def fill(self):
        self.controls.controls.clear()
        categories = Categories()
        categories.read()
        for category in categories.list:
            self.controls.controls.append(
                ft.ListTile(title=ft.Text(category.title), leading=ft.Icon(ft.icons.LIST_SHARP)))

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.controls = self.build()

    def build(self):
        return ft.ListView(expand=True, spacing=5, padding=5, auto_scroll=False, width=400,
                           height=self.page.height - 100)


def dialog(title, content, actions):
    return ft.AlertDialog(
        modal=True,
        title=ft.Text(title, width=400),
        content=content,
        actions=actions)


class SettingsDialog(ft.UserControl):
    page = None
    api_key_field = None

    def change_theme(self, e):
        self.page.theme_mode = ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        self.page.update()

    def close_dialog_settings(self, e):
        self.controls.open = False
        self.page.update()

    def save_close_dialog_settings(self, e):
        fast8tube_sql.save_settings(self.api_key_field.value, self.page.theme_mode == ft.ThemeMode.DARK)
        self.close_dialog_settings(e)

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.controls = self.build()
        self.page.update()

    def build(self):
        self.api_key_field = ft.TextField(label='Ключ google-api', password=True, can_reveal_password=True)
        self.api_key_field.value = fast8tube_data.API_KEY
        settings_dialog = dialog('Настройки', self.api_key_field, [
            ft.IconButton(icon=ft.icons.SUNNY, on_click=self.change_theme),
            ft.TextButton("Сохранить", on_click=self.save_close_dialog_settings),
            ft.TextButton("Закрыть", on_click=self.close_dialog_settings)])
        self.page.dialog = settings_dialog
        settings_dialog.open = True
        return settings_dialog


class CategoryForm(ft.UserControl):
    page = None
    category_field = None
    categories_list = None

    def save_close_dialog_add_category(self, e):
        if self.category_field.value:
            category = Category(title=self.category_field.value)
            category.write()
            self.categories_list.fill()
            self.category_field.value = ''
            self.close_dialog_add_category(e)

    def close_dialog_add_category(self, e):
        self.page.dialog.open = False
        self.page.update()

    def __init__(self, page: ft.Page, categories_list):
        super().__init__()
        self.page = page
        self.categories_list = categories_list

        self.controls = self.build()

    def build(self):
        self.category_field = ft.TextField(label='Наименование категории', width=500)
        actions = [
            ft.TextButton("Сохранить", on_click=self.save_close_dialog_add_category),
            ft.TextButton("Закрыть", on_click=self.close_dialog_add_category)]
        category_dialog = dialog(title='Добавить категорию', content=self.category_field, actions=actions)
        self.page.dialog = category_dialog
        self.page.dialog.open = True
        self.page.update()

        return category_dialog


def remove_controls(layout, controls):
    if controls.controls in layout.controls:
        layout.controls.remove(controls.controls)


def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"

    fast8tube_sql.check_database()
    page.theme_mode = ft.ThemeMode.DARK if fast8tube_data.THEME else ft.ThemeMode.LIGHT

    videos_list = VideosList(page)
    channels_list = ChannelsList(page, videos_list)
    categories_list = CategoriesList(page)
    main_column = ft.Column(expand=True, height=page.height)
    main_column.controls.append(videos_list.controls)

    def tabs_changed(e):
        if e.control.selected_index == 0:
            remove_controls(main_column, channels_list)
            remove_controls(main_column, categories_list)
            main_column.controls.append(videos_list.controls)
        elif e.control.selected_index == 1:
            remove_controls(main_column, videos_list)
            remove_controls(main_column, categories_list)
            main_column.controls.append(channels_list.controls)
        elif e.control.selected_index == 2:
            remove_controls(main_column, videos_list)
            remove_controls(main_column, channels_list)
            main_column.controls.append(categories_list.controls)
        else:
            remove_controls(main_column, videos_list)
            remove_controls(main_column, channels_list)
            remove_controls(main_column, categories_list)
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.BOOKMARK_BORDER, selected_icon=ft.icons.BOOKMARK, label="Видео"
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.BOOKMARK_BORDER),
                selected_icon_content=ft.Icon(ft.icons.BOOKMARK),
                label="Каналы",
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.BOOKMARK_BORDER),
                selected_icon_content=ft.Icon(ft.icons.BOOKMARK),
                label="Категории",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label_content=ft.Text("Настройки"),
            ),
        ],
        on_change=tabs_changed,
    )

    page.add(ft.Row([rail, main_column], expand=True, ))

    videos_list.fill()
    channels_list.fill()
    categories_list.fill()

    """
    def open_settings(e):
        SettingsDialog(page)

    def add_channel_or_category(e):
        if tabs.selected_index == 0:
            ChannelForm(page, Channel(''), channels_list)
        else:
            CategoryForm(page, categories_list)

    slide_column.controls.append(
        ft.Row([ft.FloatingActionButton(icon=ft.icons.ADD, on_click=add_channel_or_category), tabs]))
    slide_column.controls.append(channels_list.controls)
    """

    def page_resize(e):
        main_column.height = page.window_height
        page.update()

    page.on_resize = page_resize

    page.update()


def create_gui():
    ft.app(target=main_window)
