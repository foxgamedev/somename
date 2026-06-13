# client-data

Static client assets and data files, managed automatically.

Files under `client/` are served as-is. `manifest.json` lists every tracked
file with its sha256 checksum and size. Do not edit `manifest.json` by hand —
regenerate it with `make_manifest.py`.

## Update flow

```bash
# 1) put / replace files under client/ (keeping the client folder structure)
#    e.g. client/system/sysstring-e.dat

# 2) regenerate the manifest
python3 make_manifest.py client manifest.json

# 3) commit & push
git add -A && git commit -m "update" && git push
```
