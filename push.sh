#!/usr/bin/env bash
# Один рух: перегенерувати manifest.json + закомітити + запушити.
# Використання:  ./push.sh "опис змін"
# (якщо опис не вказати — буде "update")
set -e
cd "$(dirname "$0")"

echo "→ генерую manifest.json…"
python3 make_manifest.py client manifest.json

echo "→ git commit + push…"
git add -A
git commit -m "${1:-update}"
git push

echo "✓ Готово. Зачекай ~1-2 хв (кеш GitHub) і запускай лаунчер."
