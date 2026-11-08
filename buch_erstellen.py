from pathlib import Path
from html import escape
from urllib.parse import urlsplit, unquote
import re

import markdown
from markdown.treeprocessors import Treeprocessor
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
AUSGABE = ROOT / "ausgabe"
AUSGABE.mkdir(exist_ok=True)


class Bildpfade(Treeprocessor):
    def __init__(self, md, ordner):
        super().__init__(md)
        self.ordner = ordner

    def run(self, element):
        for bild in element.iter("img"):
            quelle = bild.get("src", "")
            url = urlsplit(quelle)
            if quelle and not url.scheme and not quelle.startswith("//"):
                datei = (self.ordner / unquote(url.path)).resolve()
                if not datei.is_file():
                    raise FileNotFoundError(f"Bild fehlt: {datei}")
                bild.set("src", datei.as_uri())


def umwandeln(datei):
    text = datei.read_text(encoding="utf-8-sig")
    md = markdown.Markdown(extensions=["extra"])
    md.treeprocessors.register(
        Bildpfade(md, datei.parent), "bildpfade", 5
    )
    return md.convert(text)


deckblatt = umwandeln(ROOT / "deckblatt.md")
kapitel = []
inhaltsverzeichnis = []

dateien = sorted(
    (ROOT / "kapitel").glob("*.md"),
    key=lambda datei: datei.name.casefold(),
)

for nummer, datei in enumerate(dateien, start=1):
    text = datei.read_text(encoding="utf-8-sig")
    treffer = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    titel = treffer.group(1).strip() if treffer else datei.stem
    kennung = f"kapitel-{nummer}"

    inhaltsverzeichnis.append(
        f'<li><a href="#{kennung}">{escape(titel)}</a></li>'
    )
    kapitel.append(
        f'<section class="kapitel" id="{kennung}">'
        f"{umwandeln(datei)}</section>"
    )

inhalt = (
    "<ol>" + "".join(inhaltsverzeichnis) + "</ol>"
    if dateien
    else "<p>Hier erscheinen später die Kapitel der Gruppen.</p>"
)

css = (ROOT / "buch.css").read_text(encoding="utf-8")
html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>WienGuide</title>
<style>
{css}
body {{
  font-family: Arial, "Noto Sans", "Noto Color Emoji", sans-serif;
}}
table {{
  border-collapse: collapse;
  width: 100%;
}}
th, td {{
  border: 1px solid #ccc;
  padding: 6px;
}}
</style>
</head>
<body>
<section class="deckblatt">{deckblatt}</section>
<section class="inhaltsverzeichnis">
<h1>Inhaltsverzeichnis</h1>
{inhalt}
</section>
{"".join(kapitel)}
</body>
</html>
"""

html_datei = AUSGABE / "WienGuide.html"
html_datei.write_text(html, encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(html_datei.as_uri(), wait_until="load")
    page.emulate_media(media="print")
    page.evaluate("document.fonts.ready")

    page.wait_for_function(
        "() => Array.from(document.images).every(img => img.complete)"
    )
    fehlende_bilder = page.eval_on_selector_all(
        "img",
        "(bilder) => bilder.filter(b => !b.naturalWidth).map(b => b.src)",
    )
    if fehlende_bilder:
        raise RuntimeError(f"Bilder nicht geladen: {fehlende_bilder}")

    page.pdf(
        path=str(AUSGABE / "WienGuide.pdf"),
        format="A4",
        prefer_css_page_size=True,
        print_background=True,
        display_header_footer=True,
        header_template="<span></span>",
        footer_template=(
            '<div style="width:100%;text-align:center;font-size:9px;">'
            '<span class="pageNumber"></span>'
            "</div>"
        ),
    )
    browser.close()

print("PDF erstellt: ausgabe/WienGuide.pdf")
