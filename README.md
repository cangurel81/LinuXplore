# LinuXplore

![Platform](https://img.shields.io/badge/platform-Windows-lightgrey?style=flat&logo=windows)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat&logo=python)
![License](https://img.shields.io/badge/license-AGPL--3.0-green?style=flat)

A small desktop catalog of Linux distributions. Browse 69 distros by category,
search them, and jump straight to the official website or download page.

![LinuXplore](linux.png)

## Download

[![Download for Windows](https://img.shields.io/badge/Download-LinuXplore.exe-2ea44f?style=for-the-badge&logo=windows)](https://github.com/cangurel81/LinuXplore/releases/latest/download/LinuXplore.exe)

Portable `.exe`, no installation. It is not code-signed, so Windows SmartScreen may
warn you: click **More info → Run anyway**.

## Run from source

```bash
git clone https://github.com/cangurel81/LinuXplore
cd LinuXplore
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+ and Flet 0.28.3 (pinned in `requirements.txt`). The plain `flet`
package does not ship the desktop client, which is why `requirements.txt` asks for
`flet[desktop]` — without it `python main.py` starts a server and never opens a window.

## What it does

- **69 distributions** in four categories: Daily Use, Lightweight (old PC), Pentest (Security), Server
- **Search** across name, description, category and id
- **Sorting**: catalog order, featured first, A→Z, Z→A
- **Details dialog** with RAM requirement, category and version
- **Direct links** to each project's official website and download page
- **Turkish / English** interface toggle
- **USB tool shortcuts** for Rufus and balenaEtcher

The app does not download ISO files itself. It opens the official download page in
your browser, so you always get the current image from the project's own servers.

## Project structure

```
LinuXplore/
├── main.py                  # window setup and app start
├── requirements.txt
├── linux.ico / linux.png
├── src/
│   ├── ui/app_ui.py         # Flet interface (single screen)
│   ├── logic/catalog.py     # load, search, filter, sort (no UI imports)
│   └── data/
│       ├── distros.json     # 69 records, single source of truth
│       └── locales.json     # TR/EN strings
├── tests/test_ui_contract.py # Flet contract + catalog regression tests
└── tools/check_links.py     # developer script: verify catalog URLs
```

`src/logic/catalog.py` has no Flet dependency, so the data layer can be tested or
reused on its own.

## Tests

```bash
python tests/test_ui_contract.py
```

Nine dependency-free checks (no pytest needed). They guard the two Flet traps that
make the window render **silently blank** with no traceback:

- **Never name a method `build`.** `ft.Control.build()` is a Flet hook; overriding it
  makes Flet call your method again while mounting the control, and the window stays
  empty. The UI is built in `build_ui()` and drawn from `mount()` instead.
- **Never call `page.update()` before the control is added.** The constructor does not
  touch the page; `main.py` calls `app.mount()` after `page.add(app)`.

## Adding a distribution

Append a record to `src/data/distros.json`:

```json
{
  "id": "example",
  "name": "Example Linux",
  "description_tr": "Kısa Türkçe açıklama.",
  "description_en": "Short English description.",
  "category": "Gunluk Kullanim",
  "website_url": "https://example.com",
  "download_url": "https://example.com/download/",
  "version": "Güncel",
  "hardware": "4GB RAM+",
  "icon_text": "EX",
  "best_of_year": false
}
```

Valid categories: `Gunluk Kullanim`, `Hafif (Eski PC)`, `Pentest (Guvenlik)`, `Server`.
Records with a missing or duplicate `id` are skipped at load time instead of crashing
the app.

Then check that nothing is dead:

```bash
python tools/check_links.py          # plain report
python tools/check_links.py --json   # machine-readable
```

Every URL is classified as `ok` (2xx/3xx), `engelli` (401/403/429 — bot protection, opens
fine in a browser), `kirik` (404/410/5xx — really dead, must be fixed) or `ulasilamadi`
(network/TLS error). The exit code is `0` unless a `kirik` link exists, so bot-protected
and temporarily unreachable sites do not fail a CI run.

## Building the exe

Build with `flet pack` instead of calling PyInstaller directly: it injects Flet's own
PyInstaller hook (`flet_cli/__pyinstaller/hook-flet.py`) and bundles the desktop client.
A hand-written `.spec` without that hookpath produces an exe that starts and shows a blank
window.

```bash
pip install "flet[all]==0.28.3" pyinstaller
flet pack main.py -n LinuXplore -i linux.ico -y \
  --add-data "src/data/distros.json;src/data" \
  --add-data "src/data/locales.json;src/data" \
  --add-data "linux.ico;." \
  --add-data "linux.png;."
```

Output: `dist/LinuXplore.exe` (about 83 MB, single file). The `--add-data` entries are
mandatory — without the JSON files the packaged app starts with an empty grid.

## License

GNU Affero General Public License v3.0 — see [LICENSE](LICENSE).

---

## Türkçe

Linux dağıtımlarını keşfetmek için küçük bir masaüstü kataloğu: 69 dağıtım, dört
kategori, arama, sıralama ve her projenin resmî sitesine/indirme sayfasına doğrudan
bağlantı. Arayüz Türkçe ve İngilizce arasında geçiş yapabilir.

**İndir:** [LinuXplore.exe](https://github.com/cangurel81/LinuXplore/releases/latest/download/LinuXplore.exe)
(kurulum gerekmez; imzasız olduğu için SmartScreen'de **More info → Run anyway**).

**Kaynaktan çalıştırma:**

```bash
git clone https://github.com/cangurel81/LinuXplore
cd LinuXplore
pip install -r requirements.txt
python main.py
```

**Kategoriler:** Günlük Kullanım, Hafif (Eski PC), Pentest (Güvenlik), Sunucu.

Uygulama ISO indirmez; indirme sayfasını tarayıcıda açar, böylece güncel imajı her
zaman projenin kendi sunucusundan alırsın. USB'ye yazmak için Rufus veya balenaEtcher
kısayolları kenar çubuğunda durur.

**Katkı:** `src/data/distros.json` dosyasına kayıt ekle, sonra `python tools/check_links.py`
ile bağlantıları doğrula.

**Lisans:** AGPL-3.0.
