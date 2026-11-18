"""Katalog bağlantı denetleyicisi (geliştirici aracı).

`src/data/distros.json` içindeki her dağıtımın `website_url` ve `download_url`
adreslerine istek atar ve sonucu dört sınıfa ayırır:

    ok          2xx/3xx — bağlantı çalışıyor
    engelli     401/403/429 — bot koruması (Cloudflare vb.); tarayıcıda açılır
    kirik       404/410/5xx — gerçekten ölü bağlantı, düzeltilmeli
    ulasilamadi  ağ/TLS hatası — sunucu kapalı ya da sertifika sorunlu

Uygulamanın kendisi bu betiği kullanmaz; katalog elle güncellendikten sonra ölü
bağlantı kalmadığını görmek için çalıştırılır.

Kullanım:
    python tools/check_links.py
    python tools/check_links.py --json
    python tools/check_links.py --timeout 15 --workers 8

Çıkış kodu: kırık bağlantı yoksa 0, varsa 1. (Engelli/ulaşılamayan bağlantılar
çıkış kodunu değiştirmez, yalnızca raporlanır.)
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "src", "data", "distros.json")
FIELDS = ("website_url", "download_url")
USER_AGENT = "LinuXplore-link-check/1.1 (+https://github.com/cangurel81/LinuXplore)"

BLOCKED_STATUS = (401, 403, 429)


def http_status(url, timeout):
    """Adres için durum kodu döndürür; ağ hatasında None ve hata metni."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, ""
    except urllib.error.HTTPError as error:
        # Bazı sunucular HEAD'i reddeder (403/405/501); GET ile tekrar denenir.
        if error.code in (403, 405, 501):
            return http_status_get(url, timeout)
        return error.code, ""
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return http_status_get(url, timeout, str(error))


def http_status_get(url, timeout, first_error=""):
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, ""
    except urllib.error.HTTPError as error:
        return error.code, ""
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return None, first_error or str(error)


def classify(result):
    """Sonucu ok / engelli / kirik / ulasilamadi olarak sınıflandırır."""
    status = result["status"]
    if isinstance(status, int):
        if 200 <= status < 400:
            return "ok"
        if status in BLOCKED_STATUS:
            return "engelli"
        return "kirik"
    return "ulasilamadi"


def check_one(entry, field, timeout):
    url = (entry.get(field) or "").strip()
    if not url:
        return {"id": entry.get("id"), "name": entry.get("name"), "field": field,
                "url": "", "status": None, "error": "boş"}
    status, error = http_status(url, timeout)
    return {"id": entry.get("id"), "name": entry.get("name"), "field": field,
            "url": url, "status": status, "error": error}


def main():
    parser = argparse.ArgumentParser(description="Katalogdaki bağlantıları denetler.")
    parser.add_argument("--json", action="store_true", help="sonucu JSON olarak yazdır")
    parser.add_argument("--timeout", type=float, default=10.0, help="istek zaman aşımı (saniye)")
    parser.add_argument("--workers", type=int, default=6, help="eşzamanlı istek sayısı")
    args = parser.parse_args()

    with open(CATALOG_PATH, "r", encoding="utf-8") as handle:
        catalog = json.load(handle)

    jobs = [(entry, field) for entry in catalog for field in FIELDS]
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        results = list(pool.map(lambda job: check_one(job[0], job[1], args.timeout), jobs))

    for result in results:
        result["state"] = classify(result)

    summary = {
        "total": len(results),
        "ok": sum(1 for r in results if r["state"] == "ok"),
        "engelli": sum(1 for r in results if r["state"] == "engelli"),
        "kirik": sum(1 for r in results if r["state"] == "kirik"),
        "ulasilamadi": sum(1 for r in results if r["state"] == "ulasilamadi"),
    }

    if args.json:
        payload = dict(summary)
        payload["results"] = results
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        marks = {"ok": "OK   ", "engelli": "ENGELLI", "kirik": "KIRIK", "ulasilamadi": "ULASILAMADI"}
        for result in results:
            status = result["status"] if result["status"] is not None else "-"
            detail = (" " + result["error"]) if result["error"] else ""
            print("{0} {1:>3} {2:<20} {3:<12} {4}{5}".format(
                marks[result["state"]], status, result["name"], result["field"],
                result["url"], detail
            ))
        print()
        print("{total} bağlantı: {ok} çalışıyor, {engelli} bot koruması, "
              "{kirik} kırık, {ulasilamadi} ulaşılamadı.".format(**summary))

    return 1 if summary["kirik"] else 0


if __name__ == "__main__":
    sys.exit(main())
