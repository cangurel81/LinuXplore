"""LinuXplore arayüzü.

Tek ekran: solda kategori/sıralama kenar çubuğu, sağda arama ve dağıtım kartları.
Tüm veri işi `src.logic.catalog` içinde; burada yalnızca çizim var.
"""

import json
import os
import sys
import webbrowser

import flet as ft

from src.logic import catalog

# Kategori -> (çeviri anahtarı, ikon)
CATEGORY_META = {
    catalog.CATEGORY_DAILY: ("category_daily", ft.Icons.HOME),
    catalog.CATEGORY_LIGHT: ("category_light", ft.Icons.LAPTOP),
    catalog.CATEGORY_PENTEST: ("category_pentest", ft.Icons.SECURITY),
    catalog.CATEGORY_SERVER: ("category_server", ft.Icons.STORAGE),
}

SIDEBAR_WIDTH = 262
CARD_EXTENT = 320


def data_dir():
    """Veri klasörünü döndürür (kaynak çalıştırmada ve PyInstaller exe'sinde)."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        # src/ui/app_ui.py -> proje kökü
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "src", "data")


def read_json(filename, fallback):
    path = os.path.join(data_dir(), filename)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return fallback


class LinuXploreApp(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.expand = True
        self.spacing = 0
        self._page = page
        # Kontrol sayfaya eklenene kadar page.update() çağırmıyoruz.
        self._mounted = False
        self.language = "TR"
        self.locales = read_json("locales.json", {})
        self.selected_category = catalog.ALL_CATEGORIES
        self.sort_type = "default"
        self.category_tiles = {}
        self.load_error = ""

        try:
            self.distros = catalog.load_catalog(os.path.join(data_dir(), "distros.json"))
        except (OSError, ValueError) as error:
            self.distros = []
            self.load_error = str(error)

        self.build_ui()

    def mount(self):
        """Sayfaya eklendikten sonra çağrılır: ilk çizimi yapar."""
        self._mounted = True
        self._page.update()

    # ------------------------------------------------------------------ dil

    def t(self, key):
        """Çeviri anahtarını geçerli dilde döndürür; yoksa anahtarın kendisi."""
        return self.locales.get(self.language, {}).get(key, key)

    def category_label(self, category):
        meta = CATEGORY_META.get(category)
        return self.t(meta[0]) if meta else category

    # --------------------------------------------------------------- iskelet

    def build_ui(self):
        """Arayüzü kurar.

        DİKKAT: bu metodun adı `build` olamaz. `ft.Control.build()` Flet'in kendi
        kancasıdır; ezip geçince Flet kontrolü sayfaya eklerken bu metodu tekrar
        çağırıyor ve pencere boş kalıyor.
        """
        self.search_field = ft.TextField(
            hint_text=self.t("search_hint"),
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            on_change=lambda _: self.render(),
            text_size=12,
            expand=True,
            dense=True,
        )
        self.count_text = ft.Text("", size=11, color=ft.Colors.BLUE_GREY_300)

        self.grid = ft.GridView(
            expand=True,
            max_extent=CARD_EXTENT,
            child_aspect_ratio=0.92,
            spacing=10,
            run_spacing=10,
            padding=ft.padding.only(left=20, right=20, bottom=20),
        )
        self.results_box = ft.Container(expand=True)

        self.sort_dropdown = ft.Dropdown(
            value=self.sort_type,
            text_size=11,
            dense=True,
            border_radius=8,
            options=[
                ft.dropdown.Option("default", self.t("sort_default")),
                ft.dropdown.Option("populer", self.t("sort_populer")),
                ft.dropdown.Option("az", self.t("sort_az")),
                ft.dropdown.Option("za", self.t("sort_za")),
            ],
            on_change=self.on_sort_change,
        )

        self.language_btn = ft.ElevatedButton(
            self.t("language"),
            icon=ft.Icons.TRANSLATE,
            height=34,
            on_click=self.toggle_language,
        )
        self.reload_btn = ft.ElevatedButton(
            self.t("reload"),
            icon=ft.Icons.REFRESH,
            height=34,
            on_click=self.reload_catalog,
        )

        self.category_list = ft.ListView(expand=True, spacing=2, padding=0)
        self.rebuild_categories()

        self.controls = [self.build_sidebar(), self.build_content()]
        self.render()

    def build_sidebar(self):
        return ft.Container(
            width=SIDEBAR_WIDTH,
            bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.BLUE_GREY_900),
            padding=ft.padding.symmetric(horizontal=14, vertical=16),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.COMPUTER, size=26, color=ft.Colors.BLUE_400),
                            ft.Column(
                                [
                                    ft.Text(
                                        self.t("app_title"),
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_400,
                                    ),
                                    ft.Text(
                                        self.t("app_subtitle"),
                                        size=9,
                                        color=ft.Colors.BLUE_GREY_300,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=18, color=ft.Colors.BLUE_GREY_800),
                    self.category_list,
                    ft.Divider(height=18, color=ft.Colors.BLUE_GREY_800),
                    ft.Text(
                        self.t("sort_label"),
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_300,
                    ),
                    self.sort_dropdown,
                    ft.Container(height=4),
                    self.language_btn,
                    self.reload_btn,
                    ft.Divider(height=18, color=ft.Colors.BLUE_GREY_800),
                    ft.Text(
                        self.t("usb_tools"),
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_300,
                    ),
                    ft.Row(
                        [
                            ft.TextButton(
                                self.t("rufus_btn"),
                                icon=ft.Icons.OPEN_IN_NEW,
                                on_click=lambda _: self.open_url("https://rufus.ie/"),
                            ),
                            ft.TextButton(
                                self.t("etcher_btn"),
                                icon=ft.Icons.OPEN_IN_NEW,
                                on_click=lambda _: self.open_url("https://etcher.balena.io/"),
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=6,
            ),
        )

    def build_content(self):
        return ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.BLUE_GREY_900),
            content=ft.Column(
                [
                    ft.Container(
                        padding=ft.padding.only(left=20, right=20, top=18, bottom=8),
                        content=ft.Row(
                            [self.search_field, self.count_text],
                            spacing=14,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    self.results_box,
                ],
                expand=True,
                spacing=0,
            ),
        )

    # ------------------------------------------------------------ liste çizimi

    def rebuild_categories(self):
        counts = catalog.count_by_category(self.distros)
        entries = [(catalog.ALL_CATEGORIES, self.t("category_all"), ft.Icons.LIST)]
        entries += [
            (category, self.category_label(category), icon)
            for category, (_, icon) in CATEGORY_META.items()
        ]

        self.category_tiles = {}
        self.category_list.controls = []
        for category, label, icon in entries:
            tile = ft.ListTile(
                leading=ft.Icon(icon, size=19, color=ft.Colors.BLUE_200),
                title=ft.Text(label, size=13),
                trailing=ft.Text(str(counts.get(category, 0)), size=10, color=ft.Colors.BLUE_GREY_300),
                selected=category == self.selected_category,
                selected_tile_color=ft.Colors.with_opacity(0.25, ft.Colors.BLUE_700),
                dense=True,
                on_click=lambda _, cat=category: self.select_category(cat),
            )
            self.category_tiles[category] = tile
            self.category_list.controls.append(tile)

    def make_card(self, distro):
        icon_text = distro.get("icon_text") or distro["name"][:2].upper()
        description = distro.get("description_tr") if self.language == "TR" else distro.get("description_en")
        if not description:
            description = distro.get("description_en") or distro.get("description_tr") or ""

        return ft.Container(
            bgcolor=ft.Colors.with_opacity(0.55, ft.Colors.BLUE_GREY_800),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
            border_radius=10,
            padding=14,
            on_click=lambda _, d=distro: self.open_details(d),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(
                                    icon_text,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                                width=34,
                                height=34,
                                border_radius=17,
                                bgcolor=ft.Colors.BLUE_700,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                [
                                    ft.Text(distro["name"], size=13, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        distro.get("version", ""),
                                        size=9,
                                        color=ft.Colors.BLUE_200,
                                    ),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(description, size=11, color=ft.Colors.GREY_300),
                    ft.Container(expand=True),
                    ft.Divider(height=1, color=ft.Colors.BLUE_GREY_700),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.MEMORY, size=12, color=ft.Colors.BLUE_300),
                            ft.Text(distro.get("hardware", "-"), size=10, color=ft.Colors.GREY_400),
                            ft.Container(expand=True),
                            ft.Icon(ft.Icons.CATEGORY, size=12, color=ft.Colors.GREEN_300),
                            ft.Text(
                                self.category_label(distro.get("category", "")),
                                size=10,
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.LINK,
                                tooltip=self.t("website"),
                                icon_size=18,
                                icon_color=ft.Colors.BLUE_300,
                                on_click=lambda _, d=distro: self.open_url(d.get("website_url")),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip=self.t("download_page"),
                                icon_size=18,
                                icon_color=ft.Colors.GREEN_400,
                                on_click=lambda _, d=distro: self.open_url(d.get("download_url")),
                            ),
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=6,
            ),
        )

    def build_empty_view(self):
        message = self.t("load_error").replace("{error}", self.load_error) if self.load_error else None
        return ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SEARCH_OFF, size=44, color=ft.Colors.BLUE_GREY_400),
                    ft.Text(
                        self.t("no_results_title"),
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_200,
                    ),
                    ft.Text(
                        message or self.t("no_results_hint"),
                        size=11,
                        color=ft.Colors.BLUE_GREY_300,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

    def render(self):
        """Arama + filtre + sıralamayı uygular ve ızgarayı tazeler."""
        distros = catalog.query(
            self.distros,
            text=self.search_field.value or "",
            category=self.selected_category,
            sort_type=self.sort_type,
        )
        self.grid.controls = [self.make_card(distro) for distro in distros]
        self.results_box.content = self.grid if distros else self.build_empty_view()
        self.count_text.value = self.t("results").replace("{count}", str(len(distros)))
        if self._mounted:
            self._page.update()

    # ------------------------------------------------------------- etkileşim

    def select_category(self, category):
        self.selected_category = category
        for key, tile in self.category_tiles.items():
            tile.selected = key == category
        self.render()

    def on_sort_change(self, event):
        self.sort_type = event.control.value or "default"
        self.render()

    def toggle_language(self, _=None):
        self.language = "EN" if self.language == "TR" else "TR"
        self.language_btn.text = self.t("language")
        self.reload_btn.text = self.t("reload")
        self.search_field.hint_text = self.t("search_hint")
        self.sort_dropdown.options = [
            ft.dropdown.Option("default", self.t("sort_default")),
            ft.dropdown.Option("populer", self.t("sort_populer")),
            ft.dropdown.Option("az", self.t("sort_az")),
            ft.dropdown.Option("za", self.t("sort_za")),
        ]
        self.rebuild_categories()
        self.controls = [self.build_sidebar(), self.build_content()]
        self.render()

    def reload_catalog(self, _=None):
        try:
            self.distros = catalog.load_catalog(os.path.join(data_dir(), "distros.json"))
            self.load_error = ""
        except (OSError, ValueError) as error:
            self.load_error = str(error)
            self.notify(self.t("load_error").replace("{error}", self.load_error))
        self.rebuild_categories()
        self.render()
        self.notify(self.t("reloaded").replace("{count}", str(len(self.distros))))

    def open_details(self, distro):
        description = distro.get("description_tr") if self.language == "TR" else distro.get("description_en")
        if not description:
            description = distro.get("description_en") or distro.get("description_tr") or ""

        def detail_row(label, value):
            return ft.Row(
                [
                    ft.Text(label, size=11, color=ft.Colors.BLUE_GREY_300, width=80),
                    ft.Text(value, size=11),
                ],
                spacing=8,
            )

        dialog = ft.AlertDialog(
            title=ft.Text(distro["name"], weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=440,
                content=ft.Column(
                    [
                        ft.Text(description, size=12),
                        ft.Divider(height=14),
                        detail_row(self.t("category"), self.category_label(distro.get("category", ""))),
                        detail_row(self.t("hardware"), distro.get("hardware") or "-"),
                        detail_row(self.t("version"), distro.get("version") or "-"),
                    ],
                    spacing=8,
                    tight=True,
                ),
            ),
            actions=[
                ft.TextButton(
                    self.t("website"),
                    icon=ft.Icons.PUBLIC,
                    on_click=lambda _: self.open_url(distro.get("website_url")),
                ),
                ft.TextButton(
                    self.t("download_page"),
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda _: self.open_url(distro.get("download_url")),
                ),
                ft.FilledButton(self.t("close"), on_click=lambda _: self._page.close(dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._page.open(dialog)

    def open_url(self, url):
        """Bağlantıyı varsayılan tarayıcıda açar (indirme .iso dosyası değil, sayfadır)."""
        if url:
            webbrowser.open(url)

    def notify(self, message):
        self._page.open(ft.SnackBar(ft.Text(message), duration=2500))
