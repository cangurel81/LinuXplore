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

Requires Python 3.10+ and Flet 0.28.3 (pinned in `requirements.txt`).

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
├── LinuXplore.spec          # PyInstaller build definition
├── requirements.txt
├── linux.ico / linux.png
├── src/
│   ├── ui/app_ui.py         # Flet interface (single screen)
│   ├── logic/catalog.py     # load, search, filter, sort (no UI imports)
│   └── data/
│       ├── distros.json     # 69 records, single source of truth
│       └── locales.json     # TR/EN strings
└── tools/check_links.py     # developer script: verify catalog URLs
```

`src/logic/catalog.py` has no Flet dependency, so the data layer can be tested or
reused on its own.

## Adding a distribution

Append a record to `src/data/distros.json`:

```json
{
  "id": "example",
  "name": "Example Linux",
  "description_tr": "Kısa Türkçe açıklama.",
  "description_en": "Short English description.",
  "category": "Gunluk Kullanim",
  "website_url": "https://example.org",
  "download_url": "https://example.org/download/",
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

Exit code is `0` when every URL answers with 2xx/3xx, `1` otherwise.

## Building the exe

```bash
pip install pyinstaller
pyinstaller LinuXplore.spec --noconfirm --clean
```

Output: `dist/LinuXplore.exe`. The spec bundles `src/data/*.json` and the icon; without
those entries the packaged app starts with an empty grid.

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
