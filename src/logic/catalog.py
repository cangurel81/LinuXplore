"""Katalog mantığı: JSON okuma, arama, filtreleme ve sıralama.

Bu modül arayüzden bağımsızdır (flet import etmez), böylece tek başına
test edilebilir. Arayüz yalnızca buradaki fonksiyonları çağırır.
"""

import json

CATEGORY_DAILY = "Gunluk Kullanim"
CATEGORY_LIGHT = "Hafif (Eski PC)"
CATEGORY_PENTEST = "Pentest (Guvenlik)"
CATEGORY_SERVER = "Server"

# Kenar çubuğunda görünme sırası
CATEGORIES = (CATEGORY_DAILY, CATEGORY_LIGHT, CATEGORY_PENTEST, CATEGORY_SERVER)

# "Tümü" sanal kategorisi (veride geçmez)
ALL_CATEGORIES = "Tumu"

SORTS = ("default", "populer", "az", "za")

# Arama bu alanların hepsinde yapılır
SEARCH_FIELDS = ("name", "description_tr", "description_en", "category", "id")


def load_catalog(path):
    """JSON dosyasını okur, doğrular ve temiz kayıt listesi döndürür.

    Eksik ya da tekrarlı kayıtlar sessizce atlanır; böylece elle düzenlenmiş
    bir katalog dosyası uygulamayı kilitlemez.
    """
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, list):
        raise ValueError("Katalog dosyası bir liste içermeli")

    catalog = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        distro_id = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        if not distro_id or not name or distro_id in seen:
            continue
        seen.add(distro_id)
        record = dict(item)
        record["id"] = distro_id
        record["name"] = name
        record["category"] = str(item.get("category", "")).strip() or CATEGORY_DAILY
        record["version"] = str(item.get("version", "")).strip() or "Güncel"
        record["hardware"] = str(item.get("hardware", "")).strip()
        catalog.append(record)
    return catalog


def _search_text(distro):
    parts = [str(distro.get(field, "")) for field in SEARCH_FIELDS]
    return " ".join(parts).casefold()


def search(catalog, text):
    """Ad, açıklama, kategori ve kimlik alanlarında büyük/küçük harf duyarsız arama."""
    needle = (text or "").strip().casefold()
    if not needle:
        return list(catalog)
    return [distro for distro in catalog if needle in _search_text(distro)]


def filter_by_category(catalog, category):
    if not category or category == ALL_CATEGORIES:
        return list(catalog)
    return [distro for distro in catalog if distro.get("category") == category]


def sort_distros(catalog, sort_type="default"):
    items = list(catalog)
    if sort_type == "populer":
        # Öne çıkanlar başta, kalanlar ada göre
        return sorted(
            items,
            key=lambda d: (not d.get("best_of_year", False), d["name"].casefold()),
        )
    if sort_type == "az":
        return sorted(items, key=lambda d: d["name"].casefold())
    if sort_type == "za":
        return sorted(items, key=lambda d: d["name"].casefold(), reverse=True)
    return items


def query(catalog, text="", category=ALL_CATEGORIES, sort_type="default"):
    """Arama + kategori filtresi + sıralamayı tek çağrıda uygular."""
    result = filter_by_category(catalog, category)
    result = search(result, text)
    return sort_distros(result, sort_type)


def count_by_category(catalog):
    """Kategori başına kayıt sayısı ("Tumu" dahil)."""
    counts = {ALL_CATEGORIES: len(catalog)}
    for category in CATEGORIES:
        counts[category] = 0
    for distro in catalog:
        category = distro.get("category")
        if category in counts:
            counts[category] += 1
    return counts
