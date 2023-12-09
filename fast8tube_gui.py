import flet as ft


def main_window(page: ft.Page):
    page.title = "FAST8 Tube box"
    page.theme_mode = 'dark'

    page.update()


def create_gui():
    ft.app(target=main_window)
