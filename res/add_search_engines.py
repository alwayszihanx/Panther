#!/usr/bin/env python3
# Adds the Panther custom search engines to Chromium's prepopulated list and
# sets DuckDuckGo Lite (no-AI) as the default search engine for every country.
#
# How Chromium consumes these files (version 150+):
#   * components/search_engines/prepopulated_engines.json
#       - Engines live under the top-level "elements" dict, keyed by a unique
#         engine key (e.g. "google", "bing"). IDs > 1000 are reserved for
#         distribution custom engines.
#       - This file is processed at build time by the `json_to_struct` GN rule,
#         which regenerates prepopulated_engines.{h,cc}. So editing the JSON is
#         enough; the build picks the changes up automatically.
#   * third_party/search_engines_data/resources/definitions/regional_settings.json
#       - Per-country "elements" dict. Each country has a "search_engines" list
#         of references like "&google". The FIRST entry is the default search
#         provider for that country. To make an engine the default everywhere we
#         prepend its reference to every country's list.
#
# Both JSON files are JSONC (// and /* */ comments + trailing commas), so they
# are parsed with a comment/trailing-comma aware stripper rather than json.

import json
import os
import sys

ROOT = os.environ.get("CHROMIUM_SRC", os.getcwd())

# (name, keyword, search_url) -- %s is replaced with {searchTerms}
ENGINES = [
    ("Google",                      "g",    "https://www.google.com/search?q=%s"),
    ("DuckDuckGo",                  "ddg",  "https://duckduckgo.com/?q=%s"),
    ("DuckDuckGo Lite",             "ddgl", "https://lite.duckduckgo.com/lite/?q=%s"),
    ("Brave Search",                "b",    "https://search.brave.com/search?q=%s"),
    ("Startpage",                   "sp",   "https://www.startpage.com/search?q=%s"),
    ("Kagi",                        "kg",   "https://kagi.com/search?q=%s"),
    ("Bing",                        "bing", "https://www.bing.com/search?q=%s"),
    ("Yahoo",                       "yh",   "https://search.yahoo.com/search?p=%s"),
    ("Ecosia",                      "eco",  "https://www.ecosia.org/search?q=%s"),
    ("Qwant",                       "qw",   "https://www.qwant.com/?q=%s"),
    ("Mojeek",                      "mj",   "https://www.mojeek.com/search?q=%s"),
    ("Swisscows",                   "sc",   "https://swisscows.com/web?query=%s"),
    ("MetaGer",                     "mg",   "https://metager.org/meta/meta.ger3?eingabe=%s"),
    ("SearXNG",                     "sx",   "https://searx.be/search?q=%s"),
    ("Yep Search",                  "yep",  "https://yep.com/web?q=%s"),
    ("Yandex",                      "ya",   "https://yandex.com/search/?text=%s"),
    ("Baidu",                       "bd",   "https://www.baidu.com/s?wd=%s"),
    ("Naver",                       "nv",   "https://search.naver.com/search.naver?query=%s"),
    ("AOL Search",                  "aol",  "https://search.aol.com/aol/search?q=%s"),
    ("Dogpile",                     "dp",   "https://www.dogpile.com/search/web?q=%s"),
    ("You.com",                     "you",  "https://you.com/search?q=%s"),
    ("Wikiless",                    "wk",   "https://wikiless.org/wiki/Special:Search?search=%s"),
    ("Wikipedia",                   "wiki", "https://en.wikipedia.org/w/index.php?search=%s"),
    ("Wiktionary",                  "dict", "https://en.wiktionary.org/wiki/Special:Search?search=%s"),
    ("Stack Overflow",              "so",   "https://stackoverflow.com/search?q=%s"),
    ("GitHub",                      "gh",   "https://github.com/search?q=%s&type=repositories"),
    ("GitLab",                      "gl",   "https://gitlab.com/search?search=%s"),
    ("Reddit",                      "rd",   "https://www.reddit.com/search/?q=%s"),
    ("MDN Web Docs",                "mdn",  "https://developer.mozilla.org/search?q=%s"),
    ("npm",                         "npm",  "https://www.npmjs.com/search?q=%s"),
    ("PyPI",                        "py",   "https://pypi.org/search/?q=%s"),
    ("Arch Wiki",                   "arch", "https://wiki.archlinux.org/index.php?search=%s"),
]

# The engine that becomes the default everywhere. Must match the key (without
# the "panther_" prefix) generated below for the "DuckDuckGo Lite" entry.
DEFAULT_KEY = "duckduckgo_lite"

# Prefix applied to every custom engine key so it can never collide with a
# built-in engine key (google, bing, ...).
KEY_PREFIX = "panther_"


def strip_jsonc(text):
    out = []
    i = 0
    n = len(text)
    in_str = False
    esc = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < n and text[i + 1] == '/':
            while i < n and text[i] != '\n':
                i += 1
            continue
        if c == '/' and i + 1 < n and text[i + 1] == '*':
            i += 2
            while i + 1 < n and not (text[i] == '*' and text[i + 1] == '/'):
                i += 1
            i += 2
            continue
        if c == ',':
            # skip trailing commas (outside strings)
            j = i + 1
            while j < n:
                d = text[j]
                if d in ' \t\r\n':
                    j += 1
                elif d == '/' and j + 1 < n and text[j + 1] == '/':
                    while j < n and text[j] != '\n':
                        j += 1
                elif d == '/' and j + 1 < n and text[j + 1] == '*':
                    j += 2
                    while j + 1 < n and not (text[j] == '*' and text[j + 1] == '/'):
                        j += 1
                    j += 2
                else:
                    break
            if j < n and text[j] in '}]':
                i = j
                continue
            out.append(c)
            i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def load_jsonc(path):
    # utf-8-sig transparently strips a leading BOM if present.
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.loads(strip_jsonc(f.read()))


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def favicon_of(url):
    from urllib.parse import urlparse
    host = urlparse(url).netloc
    return "https://%s/favicon.ico" % host


def safe_key(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    key = "".join(ch for ch in key if ch.isalnum() or ch == "_")
    return KEY_PREFIX + key


def main():
    pe_path = os.path.join(ROOT, "components/search_engines/prepopulated_engines.json")
    if not os.path.exists(pe_path):
        print("prepopulated_engines.json not found at %s; skipping" % pe_path)
        return

    data = load_jsonc(pe_path)
    elements = data.setdefault("elements", {})
    if not isinstance(elements, dict):
        print("ERROR: prepopulated_engines.json 'elements' is not a dict; aborting")
        sys.exit(1)

    used_ids = {e.get("id") for e in elements.values() if isinstance(e, dict)}
    used_keys = set(elements.keys())

    next_id = 1001
    key_for_default = None
    added = 0
    for name, keyword, url in ENGINES:
        base_key = safe_key(name)
        key = base_key
        suffix = 2
        while key in used_keys:
            key = "%s%d" % (base_key, suffix)
            suffix += 1
        used_keys.add(key)

        while next_id in used_ids:
            next_id += 1
        eid = next_id
        used_ids.add(eid)
        next_id += 1

        elements[key] = {
            "name": name,
            "keyword": keyword,
            "favicon_url": favicon_of(url),
            "search_url": url.replace("%s", "{searchTerms}"),
            "encoding": "UTF-8",
            "id": eid,
        }
        added += 1
        if safe_key(name) == KEY_PREFIX + DEFAULT_KEY:
            key_for_default = key

    iv = data.setdefault("int_variables", {})
    max_id = max((e["id"] for e in elements.values() if isinstance(e, dict)), default=0)
    if iv.get("kMaxPrepopulatedEngineID", 0) < max_id:
        iv["kMaxPrepopulatedEngineID"] = max_id
    iv["kCurrentDataVersion"] = int(iv.get("kCurrentDataVersion", 0)) + 1

    save_json(pe_path, data)
    print("added %d search engines to prepopulated_engines.json" % added)

    if key_for_default is None:
        print("WARNING: default engine key '%s' not found; default not changed"
              % (KEY_PREFIX + DEFAULT_KEY))
        return

    # Make the default engine the first entry for every country in
    # regional_settings.json (the first entry is the country's default).
    rs_path = os.path.join(
        ROOT,
        "third_party/search_engines_data/resources/definitions/"
        "regional_settings.json")
    if not os.path.exists(rs_path):
        print("regional_settings.json not found at %s; default not changed" % rs_path)
        return

    rs = load_jsonc(rs_path)
    rs_elements = rs.get("elements", {})
    ref = "&" + key_for_default
    changed = 0
    for country, val in rs_elements.items():
        if not isinstance(val, dict):
            continue
        engines = val.get("search_engines")
        if not isinstance(engines, list):
            continue
        # Remove any pre-existing reference so we don't duplicate it.
        engines = [e for e in engines if e != ref]
        engines.insert(0, ref)
        val["search_engines"] = engines
        changed += 1

    save_json(rs_path, rs)
    print("set '%s' as the default search engine for %d countries"
          % (key_for_default, changed))


if __name__ == "__main__":
    main()
