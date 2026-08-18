import frappe
from pathlib import Path
import polib
import subprocess

SUPPORTED_LANGUAGES = ["hi", "mr"]

def update_po_file(value, translation, language):
    po_file = (
        Path(frappe.get_app_path("citizen_connect_app"))
        / "locale"
        / f"{language}.po"
    )

    po_file.parent.mkdir(parents=True, exist_ok=True)

    po = polib.pofile(str(po_file))

    entry = po.find(value)

    if entry:
        entry.msgstr = translation
    else:
        po.append(
            polib.POEntry(
                msgid=value,
                msgstr=translation,
            )
        )

    po.save(str(po_file))

def translate_master_value(value, language):
    if not value or language == "en":
        return value

    frappe.local.lang = language
    return frappe._(value)

def compile_translation(language):
    subprocess.run(
        [
            "bench",
            "compile-po-to-mo",
            "--app",
            "citizen_connect_app",
            "--locale",
            language,
            "--force",
        ],
        check=True,
    )