"""Arayüz sözleşme testleri (bağımlılık yok, pytest gerekmez).

Neden var: Flet'in kendi metotlarını yanlışlıkla ezmek ve kontrol sayfaya
eklenmeden `page.update()` çağırmak pencereyi **sessizce boş** bırakıyor —
hata da vermiyor. Bu testler o iki tuzağı yakalar.

Çalıştırma:  python tests/test_ui_contract.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import flet as ft  # noqa: E402

from src.logic import catalog  # noqa: E402
from src.ui.app_ui import LinuXploreApp  # noqa: E402


class FakePage:
    """Gercek Flet sayfasi yerine gecen sahte sayfa: cagrilari sayar."""

    def __init__(self):
        self.updates = 0
        self.opened = []

    def update(self):
        self.updates += 1

    def open(self, control):
        self.opened.append(control)

    def close(self, control):
        if control in self.opened:
            self.opened.remove(control)


def base_names():
    """ft.Row'un tum ust siniflarindaki isimler."""
    names = set()
    for cls in ft.Row.__mro__:
        names |= set(vars(cls))
    return names


def test_flet_metotlari_ezilmiyor():
    """`build` gibi Flet kancalarini ezmek pencereyi bos birakir."""
    # Python'un kendi eklediği alanlar (__doc__, __module__, __firstlineno__ ...)
    # ve __init__ ezmesi normal; sadece gerçek Flet metotlarını arıyoruz.
    own = {n for n in vars(LinuXploreApp) if not n.startswith("__")}
    reserved = {n for n in base_names() if not n.startswith("__")}
    collisions = sorted(own & reserved)
    assert not collisions, f"Flet metodu eziliyor: {collisions}"


def test_build_metodu_yok():
    """Ozellikle `build`: ft.Control.build() kancasidir."""
    assert "build" not in vars(LinuXploreApp), "build() ft.Control.build()'i eziyor"
    assert hasattr(LinuXploreApp, "build_ui"), "build_ui() yok"


def test_constructor_sayfayi_guncellemiyor():
    """page.update() kontrol sayfaya eklenmeden cagrilmamali."""
    page = FakePage()
    LinuXploreApp(page)
    assert page.updates == 0, "constructor icinde page.update() cagriliyor"


def test_mount_tek_guncelleme():
    page = FakePage()
    app = LinuXploreApp(page)
    app.mount()
    assert page.updates == 1, f"mount tek update yapmali, {page.updates} yapti"


def test_katalog_yuklendi():
    page = FakePage()
    app = LinuXploreApp(page)
    assert app.load_error == "", f"katalog yukleme hatasi: {app.load_error}"
    assert len(app.distros) == 69, f"69 kayit bekleniyordu, {len(app.distros)} geldi"
    assert len(app.grid.controls) == 69, f"69 kart bekleniyordu, {len(app.grid.controls)}"


def test_kategori_filtresi():
    page = FakePage()
    app = LinuXploreApp(page)
    app.mount()
    for category in catalog.CATEGORIES:
        app.select_category(category)
        beklenen = len(catalog.filter_by_category(app.distros, category))
        assert len(app.grid.controls) == beklenen, f"{category}: {len(app.grid.controls)} != {beklenen}"
    app.select_category(catalog.ALL_CATEGORIES)
    assert len(app.grid.controls) == 69


def test_arama_ve_siralama():
    page = FakePage()
    app = LinuXploreApp(page)
    app.mount()
    app.search_field.value = "ubuntu"
    app.render()
    assert len(app.grid.controls) >= 1, "ubuntu aramasi bos dondu"

    app.search_field.value = "zzzz-olmayan-dagitim"
    app.render()
    assert len(app.grid.controls) == 0

    app.search_field.value = ""
    app.sort_type = "az"
    app.render()
    assert len(app.grid.controls) == 69


def test_dil_degistirme():
    page = FakePage()
    app = LinuXploreApp(page)
    app.mount()
    ilk = app.language
    app.toggle_language()
    assert app.language != ilk
    assert len(app.grid.controls) == 69, "dil degisince kartlar kayboldu"
    app.toggle_language()
    assert app.language == ilk


def test_bos_arama_gorunumu():
    page = FakePage()
    app = LinuXploreApp(page)
    app.mount()
    app.search_field.value = "zzzz-olmayan-dagitim"
    app.render()
    assert app.results_box.content is not app.grid, "sonuc yokken bos gorunum gelmeli"


def main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    gecen = 0
    hatalar = []
    for name, func in tests:
        try:
            func()
            gecen += 1
            print(f"  GECTI  {name}")
        except AssertionError as error:
            hatalar.append((name, str(error)))
            print(f"  KALDI  {name}: {error}")
        except Exception as error:  # noqa: BLE001
            hatalar.append((name, f"{type(error).__name__}: {error}"))
            print(f"  HATA   {name}: {type(error).__name__}: {error}")

    print(f"\n{gecen}/{len(tests)} test gecti")
    return 0 if not hatalar else 1


if __name__ == "__main__":
    sys.exit(main())
