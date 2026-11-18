"""LinuXplore giriş noktası.

Pencereyi hazırlar, arayüzü ekler ve flet uygulamasını başlatır.
"""

import os
import sys

import flet as ft

from src.ui.app_ui import LinuXploreApp

APP_TITLE = "LinuXplore"
WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 760


def icon_path():
    """Pencere simgesinin yolunu döndürür (exe içinde de çalışır)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "linux.ico")
    return path if os.path.exists(path) else None


def main(page: ft.Page):
    page.title = APP_TITLE
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)

    # Pencere ayarları masaüstünde geçerli; web modunda sessizce yok sayılır.
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.min_width = 900
    page.window.min_height = 600
    icon = icon_path()
    if icon:
        page.window.icon = icon

    app = LinuXploreApp(page)
    page.add(app)
    # Kontrol sayfaya eklendikten sonra ilk çizimi yap.
    # (Eklenmeden önce page.update() çağırmak Flet 0.28'de kilitlenmeye yol açıyor.)
    app.mount()


if __name__ == "__main__":
    ft.app(main)
