#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерує manifest.json для Ember Launcher (інкрементально).

Сканує теку клієнта й записує manifest.json: для кожного файлу — відносний
шлях, sha256, розмір. Хеші кешуються у .hashcache.json: файл перехешовується
лише якщо змінився розмір або час модифікації.

ВИНЯТКИ (EXCLUDE_BASENAMES): особисті налаштування гравця та сміття не
потрапляють у маніфест, щоб лаунчер їх НЕ перезаписував тестерам.

Використання:
    python3 make_manifest.py <тека_клієнта> <вихід_manifest.json>
    (без аргументів: ./client -> ./manifest.json)
"""
import sys, os, json, hashlib, datetime

# Не роздавати ці файли (особисті налаштування / тимчасове). Порівняння без регістру.
EXCLUDE_BASENAMES = {
    "user.ini",        # клавіші, графіка, особисті опції гравця
    "option.ini",      # особисті опції
    "running.ini",     # лок-файл запущеного клієнта
    "put-system-here.txt",
    ".ds_store",
    ".hashcache.json",
}

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    client_dir = sys.argv[1] if len(sys.argv) > 1 else "client"
    out = sys.argv[2] if len(sys.argv) > 2 else "manifest.json"
    if not os.path.isdir(client_dir):
        print(f"Немає теки '{client_dir}'.")
        sys.exit(1)

    cache_path = os.path.join(os.path.dirname(os.path.abspath(out)) or ".", ".hashcache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            cache = json.load(open(cache_path, encoding="utf-8"))
        except Exception:
            cache = {}

    files, newcache, rehashed, skipped = [], {}, 0, 0
    for root, _, names in os.walk(client_dir):
        for n in names:
            if n.lower() in EXCLUDE_BASENAMES:
                skipped += 1
                continue
            full = os.path.join(root, n)
            rel = os.path.relpath(full, client_dir).replace(os.sep, "/")
            st = os.stat(full)
            c = cache.get(rel)
            if c and c.get("size") == st.st_size and abs(c.get("mtime", -1) - st.st_mtime) < 1e-6:
                digest = c["sha256"]
            else:
                digest = sha256(full); rehashed += 1
            newcache[rel] = {"size": st.st_size, "mtime": st.st_mtime, "sha256": digest}
            files.append({"path": rel, "sha256": digest, "size": st.st_size})

    files.sort(key=lambda x: x["path"])
    manifest = {"version": datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"), "files": files}
    json.dump(manifest, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(newcache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Записано {out}: {len(files)} файл(ів) (перехешовано {rehashed}, пропущено винятків {skipped}), версія {manifest['version']}")

if __name__ == "__main__":
    main()
