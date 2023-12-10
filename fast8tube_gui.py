import flet as ft
import fast8tube_db as f8db


def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"
    page.theme_mode = ft.ThemeMode.DARK

    def add_chanel(e):
        if len(new_channel_name.value) > 1:
            f8db.add_channel(new_channel_name.value, new_channel_name.value)

    def update_videos(e):
        print(e.data)
        #videos = f8db.get_videos(e.control.title.value) #['youtube_id'])

    new_channel_name = ft.TextField(label='Введите id добавляемого канала')

    page.add(
        ft.Row([
            new_channel_name,
            ft.FloatingActionButton(ft.icons.ADD, on_click=add_chanel)
        ])
    )

    channels_column = ft.Column(
        auto_scroll=False,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=1
    )
    videos_column = ft.Column(
        auto_scroll=False,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=1
    )

    channels = f8db.get_channels()
    page.add(
        ft.Row([
            channels_column,
            videos_column
        ])
    )

    for channel in channels:
        channels_column.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.ALBUM),
                                title=ft.Text(channel['youtube_id']),
                                subtitle=ft.Text(channel['name'])
                            ),
                            ft.Row(
                                [ft.TextButton("update", on_click=update_videos, data=channel['youtube_id']), ft.TextButton("delete")],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ]
                    ),
                    width=400,
                    padding=10,
                )
            )
        )
    page.update()


def create_gui():
    ft.app(target=main_window)
