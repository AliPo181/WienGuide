"""Ein gemeinsames, portables Buch aus Deckblatt und allen Kapiteln bauen."""
from __future__ import annotations

import argparse
import base64
import io
import json
import logging
import re
from collections import Counter
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
from PIL import Image, ImageOps
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent


class Buch:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.hinweise: list[str] = []
        self.bildfehler: list[str] = []
        self.bilder = 0
        self.cache: dict[Path, str] = {}

    def hinweis(self, text: str):
        if text not in self.hinweise:
            self.hinweise.append(text)

    def bild(self, quelle: str, datei: Path) -> str:
        quelle = quelle.strip().replace('\\', '/')
        url = urlsplit(quelle)
        if url.scheme or quelle.startswith('//'):
            raise ValueError('Bitte das Bild lokal im Ordner bilder/ ablegen')
        pfad = unquote(url.path)
        kandidaten = [datei.parent / pfad, self.root / pfad.lstrip('/')]
        for kandidat in kandidaten:
            kandidat = kandidat.resolve()
            if not kandidat.is_relative_to(self.root):
                continue
            if kandidat.is_file():
                break
            # Nur einen eindeutigen Pfad mit abweichender Schreibweise korrigieren.
            relativ = kandidat.relative_to(self.root).as_posix().casefold()
            treffer = [p for p in self.root.rglob('*') if p.is_file()
                       and p.relative_to(self.root).as_posix().casefold() == relativ]
            if len(treffer) == 1:
                kandidat = treffer[0]
                self.hinweis(f'{datei.name}: Groß-/Kleinschreibung im Bildpfad prüfen: {quelle}')
                break
        else:
            raise ValueError(f'Bilddatei nicht gefunden: {quelle}')
        if kandidat not in self.cache:
            with Image.open(kandidat) as original:
                original.seek(0)  # Ein gedrucktes Buch zeigt das erste GIF-Bild.
                bild = ImageOps.exif_transpose(original)
                bild.thumbnail((2400, 3200), Image.Resampling.LANCZOS)
                transparent = 'A' in bild.getbands() or 'transparency' in bild.info
                bild = bild.convert('RGBA' if transparent else 'RGB')
                daten = io.BytesIO()
                fmt = 'PNG' if transparent else 'JPEG'
                bild.save(daten, format=fmt, **({} if transparent else {'quality': 92}))
                mime = 'image/png' if transparent else 'image/jpeg'
                self.cache[kandidat] = f'data:{mime};base64,' + base64.b64encode(daten.getvalue()).decode()
        self.bilder += 1
        return self.cache[kandidat]

    def render(self, datei: Path, kennung: str) -> tuple[str, str]:
        md = markdown.Markdown(extensions=['extra', 'toc'])
        roh = md.convert(datei.read_text(encoding='utf-8-sig'))
        erster_titel = next((t for t in md.toc_tokens if t['level'] == 1), None)
        titel = erster_titel['name'] if erster_titel else datei.stem
        # Formatierung und HTML-Entities aus dem TOC-Titel entfernen.
        parser = Text()
        parser.feed(titel)
        titel = ''.join(parser.text).strip()
        if titel.startswith('[') and titel.endswith(']'):
            titel = titel[1:-1].strip()
        if not erster_titel and kennung != 'cover':
            self.hinweis(f'{datei.name}: Kapitelüberschrift mit # fehlt; Dateiname verwendet.')
        if 'Euer selbst gewählter Kapiteltitel' in titel:
            titel = datei.stem
            self.hinweis(f'{datei.name}: Bitte noch einen eigenen Kapiteltitel eintragen.')
        if 'Bildplatzhalter' in roh or 'https://example.org' in roh:
            self.hinweis(f'{datei.name}: Enthält noch Vorlagen-Platzhalter.')
        parser = BilderHTML(self, datei, kennung)
        parser.feed(roh)
        parser.close()
        return titel, ''.join(parser.ausgabe)

    def kapiteldateien(self) -> list[Path]:
        dateien = []
        for datei in sorted((self.root / 'kapitel').rglob('*'),
                            key=lambda p: p.relative_to(self.root).as_posix().casefold()):
            if not datei.is_file() or any(p.startswith('.') for p in datei.relative_to(self.root / 'kapitel').parts):
                continue
            if datei.suffix.casefold() in {'.md', '.markdown'}:
                dateien.append(datei)
            elif not datei.suffix:
                try:
                    text = datei.read_text(encoding='utf-8-sig')
                except (UnicodeError, OSError):
                    continue
                if re.search(r'^#\s+\S', text, re.M):
                    dateien.append(datei)
                    self.hinweis(f'{datei.name}: Ohne .md-Endung gefunden und trotzdem aufgenommen.')
        return dateien


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []

    def handle_data(self, data):
        self.text.append(data)


class BilderHTML(HTMLParser):
    """Auch Bilder in direkt eingegebenem HTML bearbeiten; Kommentare ignorieren."""
    def __init__(self, buch: Buch, datei: Path, kennung: str):
        super().__init__(convert_charrefs=False)
        self.buch, self.datei, self.kennung = buch, datei, kennung
        self.ausgabe = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            quelle = attrs.get('src') or ''
            try:
                attrs['src'] = self.buch.bild(quelle, self.datei)
                attrs.pop('width', None)
                attrs.pop('height', None)
            except (ValueError, OSError, Image.DecompressionBombError) as fehler:
                meldung = f'{self.datei.relative_to(self.buch.root)}: {quelle} - {fehler}'
                self.buch.bildfehler.append(meldung)
                self.ausgabe.append('<span class="bild-fehlt">Bild noch nicht verfügbar: '
                                     + escape(attrs.get('alt') or quelle) + '</span>')
                return
        if attrs.get('id'):
            attrs['id'] = self.kennung + '-' + attrs['id']
        if tag == 'a' and (attrs.get('href') or '').startswith('#'):
            attrs['href'] = '#' + self.kennung + '-' + attrs['href'][1:]
        self.ausgabe.append('<' + tag + ''.join(
            ' ' + k if v is None else f' {k}="{escape(v, quote=True)}"'
            for k, v in attrs.items()) + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag not in {'img', 'br', 'hr', 'input', 'meta', 'link'}:
            self.ausgabe.append(f'</{tag}>')

    def handle_data(self, data):
        self.ausgabe.append(data)

    def handle_entityref(self, name):
        self.ausgabe.append(f'&{name};')

    def handle_charref(self, name):
        self.ausgabe.append(f'&#{name};')

    def handle_comment(self, data):
        pass


def bauen(root: Path = ROOT, strict: bool = False, nur_html: bool = False) -> dict:
    buch = Buch(root)
    ausgabe = buch.root / 'ausgabe'
    ausgabe.mkdir(exist_ok=True)
    pdf = ausgabe / 'WienGuide.pdf'
    pdf.unlink(missing_ok=True)  # Kein altes PDF nach einem fehlgeschlagenen Lauf anbieten.
    _, deckblatt = buch.render(buch.root / 'deckblatt.md', 'cover')
    kapitel, toc, infos = [], [], []
    for n, datei in enumerate(buch.kapiteldateien(), 1):
        kennung = f'kapitel-{n}'
        titel, inhalt = buch.render(datei, kennung)
        toc.append(f'<li><a href="#{kennung}"><span class="toc-nr">{n:02d}</span> '
                   f'<span class="toc-titel">{escape(titel)}</span></a></li>')
        kapitel.append(f'<section class="kapitel" id="{kennung}">{inhalt}</section>')
        infos.append({'datei': datei.relative_to(buch.root).as_posix(), 'titel': titel})
    for titel, anzahl in Counter(x['titel'] for x in infos).items():
        if anzahl > 1:
            buch.hinweis(f'Der Kapiteltitel „{titel}“ kommt {anzahl}-mal vor; alle Beiträge bleiben enthalten.')
    css = (buch.root / 'buch.css').read_text(encoding='utf-8')
    inhalt = '<ol>' + ''.join(toc) + '</ol>' if toc else '<p>Die Kapitel folgen.</p>'
    html = ('<!doctype html><html lang="de"><head><meta charset="utf-8">'
            '<title>Wien entdecken - Reiseführer</title><style>' + css + '</style></head><body>'
            '<section class="deckblatt">' + deckblatt + '</section>'
            '<nav class="inhaltsverzeichnis"><h1>Inhaltsverzeichnis</h1>' + inhalt + '</nav>'
            + ''.join(kapitel) + '</body></html>')
    (ausgabe / 'WienGuide.html').write_text(html, encoding='utf-8')
    bericht = {'kapitel': infos, 'eingebundene_bilder': buch.bilder,
               'hinweise': buch.hinweise, 'bildfehler': buch.bildfehler}
    (ausgabe / 'Bauprotokoll.json').write_text(json.dumps(bericht, ensure_ascii=False, indent=2), encoding='utf-8')
    for hinweis in buch.hinweise:
        logging.warning(hinweis)
    for fehler in buch.bildfehler:
        logging.warning(fehler)
    if strict and buch.bildfehler:
        raise ValueError('Aktive Bildverweise fehlerhaft; siehe ausgabe/Bauprotokoll.json.')
    if not nur_html:
        HTML(string=html, base_url=str(buch.root)).write_pdf(pdf, optimize_images=True)
    print(f'{len(infos)} Kapitel, {buch.bilder} Bilder, {len(buch.bildfehler)} Bildfehler.')
    return bericht


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict-images', action='store_true', help='Bei fehlerhaften Bildverweisen abbrechen (PR-Prüfung).')
    parser.add_argument('--html-only', action='store_true', help='Nur HTML und Bauprotokoll erstellen.')
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    bauen(strict=args.strict_images, nur_html=args.html_only)
