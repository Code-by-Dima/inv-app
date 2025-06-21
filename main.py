import flet as ft
from db import init_db
from ui import main_view


def main(page: ft.Page):
    page.title = "Інвентаризація"
    # Використовуємо Material 3 (fallback на hex, оскільки ft.colors може бути відсутнім у вашій версії Flet)
    page.theme = ft.Theme(color_scheme_seed="#2196F3", use_material3=True)
    page.theme_mode = ft.ThemeMode.LIGHT
    # AppBar з назвою та іконкою
    page.appbar = ft.AppBar(title=ft.Text("Інвентаризація"), center_title=False, bgcolor="#42A5F5")
    # Адаптивний розмір вікна
    page.window_width = 1600
    page.window_height = 900
    page.window_min_width = 1600
    page.window_max_width = 1600
    page.window_min_height = 900
    page.window_max_height = 900
    page.window_maximized = False  # Забороняємо повноекранний режим
    page.window_resizable = False  # Забороняємо зміну розміру
    init_db()
    main_view(page)
    # Останній update після побудови інтерфейсу
    page.update()
    # Додаткове оновлення не потрібне, габарити вже встановлено

if __name__ == "__main__":
    ft.app(target=main)
