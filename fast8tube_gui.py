import flet as ft
import fast8tube_db as f8db

def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"
    page.theme_mode = ft.ThemeMode.DARK

    def add_chanel(e):
        f8db.add_channel(new_channel_name.value, new_channel_name.value)

    new_channel_name = ft.TextField(label='Введите id добавляемого канала')

    page.add(
        ft.Row([
            new_channel_name,
            ft.FloatingActionButton(ft.icons.ADD, on_click=add_chanel)
        ])
    )

    videos = ft.Column(
        auto_scroll=False,
        scroll=ft.ScrollMode.ADAPTIVE,
        #padding=10,
        expand=1,
        #runs_count=10,
        #max_extent=400,
        #child_aspect_ratio=5.0,
        #spacing=50,
        #run_spacing=5
    )

    channels = f8db.get_channels()
    page.add(videos)
    for channel in channels:
        videos.controls.append(
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
                                [ft.TextButton("update"), ft.TextButton("delete")],
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
