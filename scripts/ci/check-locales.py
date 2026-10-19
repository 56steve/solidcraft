#!/usr/bin/env python3
"""Validate translation catalogs without CI (mirrors i18n.rs catalogs_have_valid_ids_and_matching_placeholders).
Usage: python3 -I scripts/ci/check-locales.py <repo-dir> [file ...]   (default: every assets/locales/*.json except en.json)
Checks: valid JSON object of strings, no duplicate keys, every key exists in en.json, placeholders
{name} identical to English, keys in the same sorted order as the repo uses."""
import json, re, sys, pathlib
root = pathlib.Path(sys.argv[1]); loc = root / "assets/locales"
def load(p):
    def hook(pairs):
        keys = [k for k, _ in pairs]
        if len(keys) != len(set(keys)): raise ValueError("duplicate key")
        return dict(pairs)
    return json.loads(p.read_text(encoding="utf-8"), object_pairs_hook=hook), list(json.loads(p.read_text(encoding="utf-8")).keys())
ph = lambda s: sorted(re.findall(r"\{[A-Za-z_][A-Za-z0-9_]*\}", s))
en, _ = load(loc / "en.json")
files = [root / f for f in sys.argv[2:]] or sorted(p for p in loc.glob("*.json") if p.name != "en.json")
bad = 0
for p in files:
    try:
        d, order = load(p)
    except Exception as e:
        print(f"{p.name}: invalid JSON: {e}"); bad += 1; continue
    errs = []
    if not d: errs.append("empty catalog")
    for k, v in d.items():
        if not isinstance(v, str): errs.append(f"non-string value: {k!r}")
        elif k not in en: errs.append(f"unknown key: {k!r}")
        elif ph(v) != ph(en[k]): errs.append(f"placeholders differ: {k!r}: {ph(v)} vs {ph(en[k])}")
    if order != sorted(order): errs.append("keys not sorted")
    for e in errs[:20]: print(f"{p.name}: {e}")
    bad += bool(errs)
print("OK" if not bad else f"{bad} catalog(s) failed"); sys.exit(1 if bad else 0)
