import frappe
from frappe.utils import cint

# This module's own dotted path, used for frappe.enqueue targets. Derived, not
# hardcoded, so moving the file never leaves a stale string behind.
MODULE = __name__

# --------------------------------------------------------------------------
# Registry - the only thing you edit when adding a new translatable master
# --------------------------------------------------------------------------
# doctype -> fieldname whose value is shown in Link fields.
# For autoname-by-field doctypes (e.g. Category via catalogue_name) this equals
# `name`, which is what Translate Link Fields renders.
TRANSLATABLE_MASTERS = {
    "Category": "catalogue_name",
    "Country": "country_name",
    "Geography L1": "geo_l1",
    "Geography L2": "geo_l2",
    "Badge": "title",
}

DEFAULT_LANGUAGES = ["hi"]
MT_BATCH_SIZE = 50      # strings per machine-translation call
INSERT_CHUNK = 500      # rows per commit
SOURCE_LANG = "en"


def get_target_languages() -> list[str]:
    return frappe.conf.get("master_translation_languages") or DEFAULT_LANGUAGES


# --------------------------------------------------------------------------
# What should exist, and what is missing
# --------------------------------------------------------------------------
def get_translables():
    for doctype, fieldname in TRANSLATABLE_MASTERS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        rows = frappe.get_all(doctype, fields=["name", fieldname],
                              limit_page_length=0, ignore_permissions=True)
        for row in rows:
            value = (row.get(fieldname) or "").strip()
            if value:
                yield doctype, row["name"], value

def _existing_translation_pairs(languages: list[str]) -> set:
    rows = frappe.get_all("Translation",
                          filters={"language": ("in", languages)},
                          fields=["source_text", "language"],
                          limit_page_length=0, ignore_permissions=True)
    return {((r["source_text"] or "").strip(), r["language"]) for r in rows}


def get_missing_translations(languages: list[str]) -> list[dict]:
    existing = _existing_translation_pairs(languages)
    seen, missing = set(), []

    for doctype, docname, value in get_translables():
        for lang in languages:
            key = (value, lang)
            if key in existing or key in seen:
                continue      # same string in two masters -> one row
            seen.add(key)
            missing.append({"reference_doctype": doctype, "reference_name": docname,
                            "source_text": value, "language": lang})
    return missing


# --------------------------------------------------------------------------
# Coverage
# --------------------------------------------------------------------------
@frappe.whitelist()
def coverage(languages=None, include_gaps=0) -> dict:
    """Per-doctype, per-language counts. Pass include_gaps=1 for the item list
    (can be large - it is every untranslated value)."""
    if isinstance(languages, str):
        languages = frappe.parse_json(languages)
    languages = languages or get_target_languages()
    include_gaps = cint(include_gaps)

    index = {}
    for r in frappe.get_all("Translation",
                            filters={"language": ("in", languages)},
                            fields=["source_text", "language", "source", "reviewed"],
                            limit_page_length=0, ignore_permissions=True):
        index[((r["source_text"] or "").strip(), r["language"])] = r

    buckets, gaps = {}, []
    for doctype, docname, value in get_translables():
        for lang in languages:
            b = buckets.setdefault((doctype, lang), {
                "doctype": doctype, "language": lang, "total": 0,
                "translated": 0, "machine": 0, "reviewed": 0, "missing": 0,
            })
            b["total"] += 1
            hit = index.get((value, lang))
            if hit:
                b["translated"] += 1
                if cint(hit.get("reviewed")):
                    b["reviewed"] += 1
                elif (hit.get("source") or "") == "machine":
                    b["machine"] += 1
            else:
                b["missing"] += 1
                if include_gaps:
                    gaps.append({"doctype": doctype, "name": docname,
                                 "source_text": value, "language": lang})

    summary = []
    for b in buckets.values():
        b["pct"] = round(100.0 * b["translated"] / b["total"], 1) if b["total"] else 0.0
        summary.append(b)
    summary.sort(key=lambda x: (x["language"], x["doctype"]))

    out = {"languages": languages, "summary": summary}
    if include_gaps:
        out["gaps"] = gaps
    return out


def print_coverage():
    """bench --site <site> execute citizen_connect_app.utils.translations.print_coverage"""
    print(f"{'DocType':<20}{'Lang':<6}{'Total':>7}{'Done':>7}{'Review':>8}{'Missing':>9}{'%':>8}")
    print("-" * 65)
    for r in coverage()["summary"]:
        print(f"{r['doctype']:<20}{r['language']:<6}{r['total']:>7}{r['translated']:>7}"
              f"{r['reviewed']:>8}{r['missing']:>9}{r['pct']:>7}%")


# --------------------------------------------------------------------------
# Machine translation
# --------------------------------------------------------------------------
def translate_batch(texts: list[str], target_lang: str) -> list[str]:
    """Returns a list the same length as `texts`; "" means failed - caller skips.

    Swap the provider here if LibreTranslate quality is not good enough.
    """
    try:
        return _mt_libretranslate(texts, target_lang)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "master_translation: MT batch failed")
        return ["" for _ in texts]


def _mt_libretranslate(texts: list[str], target_lang: str) -> list[str]:
    import requests
    url = "http://localhost:5000/translate"
    payload = {"q": texts, "source": SOURCE_LANG, "target": target_lang, "format": "text"}
    if frappe.conf.get("libretranslate_api_key"):
        payload["api_key"] = frappe.conf.get("libretranslate_api_key")
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    out = resp.json().get("translatedText")
    if isinstance(out, str):
        out = [out]
    return [(o or "").strip() for o in out]

def translate(target_languae:str, source_text:str) -> str:
    if not source_text or not target_languae or target_languae == SOURCE_LANG or source_text.strip() == "":
        return source_text
    import requests
    url = "http://localhost:5000/translate"
    payload = {"q": source_text, "source": SOURCE_LANG, "target": target_languae, "format": "text"}
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    out = resp.json().get("translatedText")
    if isinstance(out, str):
        out = [out]
    return [(o or "").strip() for o in out]

# --------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------
def _insert_translation(row: dict, translated: str):
    doc = frappe.new_doc("Translation")
    doc.language = row["language"]
    doc.source_text = row["source_text"]
    doc.translated_text = translated
    doc.reference_doctype = row.get("reference_doctype")   # custom fields
    doc.reference_name = row.get("reference_name")
    doc.source = "machine"
    doc.reviewed = 0
    doc.flags.ignore_permissions = True
    doc.flags.ignore_links = True
    doc.insert()


def clear_translation_cache():
    """Once per run. Never inside a row loop - it rebuilds the whole dict."""
    try:
        from frappe.translate import clear_cache as _clear
        _clear()
    except Exception:
        frappe.clear_cache()


# --------------------------------------------------------------------------
# The pipeline
# --------------------------------------------------------------------------
def sync_missing(languages: list[str] | None = None, limit: int | None = None) -> dict:

    languages = languages or get_target_languages()
    missing = get_missing_translations(languages)
    if limit:
        missing = missing[:cint(limit)]
    if not missing:
        return {"attempted": 0, "written": 0, "failed": 0}

    by_lang = {}
    for row in missing:
        by_lang.setdefault(row["language"], []).append(row)

    written = failed = pending = 0
    for lang, rows in by_lang.items():
        for i in range(0, len(rows), MT_BATCH_SIZE):
            chunk = rows[i:i + MT_BATCH_SIZE]
            results = translate_batch([r["source_text"] for r in chunk], lang)
            for row, translated in zip(chunk, results):
                if not translated or translated == row["source_text"]:
                    failed += 1
                    continue
                try:
                    _insert_translation(row, translated)
                    written += 1
                    pending += 1
                except frappe.DuplicateEntryError:
                    pass          # raced another worker - fine
                except Exception:
                    failed += 1
                    frappe.log_error(frappe.get_traceback(),
                                     "master_translation: insert failed")
            if pending >= INSERT_CHUNK:
                frappe.db.commit()
                pending = 0

    frappe.db.commit()
    clear_translation_cache()
    return {"attempted": len(missing), "written": written, "failed": failed}


@frappe.whitelist()
def enqueue_sync(languages=None):
    """Run the backfill in the background. Never do it in a web request."""
    if isinstance(languages, str):
        languages = frappe.parse_json(languages)
    frappe.enqueue(f"{MODULE}.sync_missing",
                   queue="long", timeout=7200, job_name="master_translation_sync",
                   languages=languages)
    return {"queued": True}


# --------------------------------------------------------------------------
# Doc events
# --------------------------------------------------------------------------
def on_master_update(doc, method=None):
    """after_insert / on_update. Queues one small job, not a full scan."""
    fieldname = TRANSLATABLE_MASTERS.get(doc.doctype)
    if not fieldname:
        return
    value = (doc.get(fieldname) or "").strip()
    if not value:
        return
    frappe.enqueue(f"{MODULE}.translate_one",
                   queue="short", enqueue_after_commit=True,
                   doctype=doc.doctype, docname=doc.name, value=value)


def translate_one(doctype: str, docname: str, value: str, languages=None):
    languages = languages or get_target_languages()
    todo = [lang for lang in languages
            if not frappe.db.exists("Translation", {"source_text": value, "language": lang})]
    if not todo:
        return
    for lang in todo:
        results = translate_batch([value], lang)
        if results and results[0] and results[0] != value:
            try:
                _insert_translation({"reference_doctype": doctype,
                                     "reference_name": docname,
                                     "source_text": value, "language": lang},
                                    results[0])
            except frappe.DuplicateEntryError:
                pass
    frappe.db.commit()
    clear_translation_cache()


def on_master_rename(doc, method=None, *args, **kwargs):
    """Renaming a master orphans its translations, because source_text IS the
    old name. Repoint them.

    Frappe calls after_rename as run_method("after_rename", olddn, newdn, merge),
    so the names arrive positionally. Verify the arity on your v16 build.
    """
    old_name = kwargs.get("old_name") or (args[0] if len(args) > 0 else None)
    new_name = kwargs.get("new_name") or (args[1] if len(args) > 1 else None)
    if not old_name or not new_name or old_name == new_name:
        return
    if doc.doctype not in TRANSLATABLE_MASTERS:
        return

    names = frappe.get_all("Translation", filters={"source_text": old_name},
                           pluck="name", limit_page_length=0)
    for n in names:
        frappe.db.set_value("Translation", n,
                            {"source_text": new_name, "reference_name": new_name},
                            update_modified=False)
    if names:
        frappe.db.commit()
        clear_translation_cache()


# --------------------------------------------------------------------------
# One-time setup
# --------------------------------------------------------------------------
CUSTOM_FIELDS = {
    "Translation": [
        {"fieldname": "cc_section", "fieldtype": "Section Break",
         "label": "Master Data Provenance", "insert_after": "translated_text"},
        {"fieldname": "reference_doctype", "fieldtype": "Link", "options": "DocType",
         "label": "Reference DocType", "insert_after": "cc_section", "read_only": 1},
        {"fieldname": "reference_name", "fieldtype": "Data",
         "label": "Reference Name", "insert_after": "reference_doctype", "read_only": 1},
        {"fieldname": "source", "fieldtype": "Select", "options": "\nmanual\nmachine",
         "default": "manual", "label": "Source", "insert_after": "reference_name"},
        {"fieldname": "reviewed", "fieldtype": "Check", "label": "Reviewed",
         "insert_after": "source",
         "description": "The pipeline never overwrites an existing row."},
    ]
}


def install_custom_fields():
    """Idempotent. Wired to after_install and after_migrate in hooks.py, so it
    runs on fresh installs AND on sites that already have the app.

    Manual run:
      bench --site <site> execute \
        citizen_connect_app.utils.translations.install_custom_fields
    """
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
    # No commit here - bench install/migrate commits for us, and committing
    # mid-migration can cut a patch in half. Only commit on a manual run.