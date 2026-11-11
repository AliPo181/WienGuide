# Buchausgabe und Bildprüfung

Die Dateien unter `kapitel/` werden in einem gemeinsamen Buch zusammengeführt. Jedes Kapitel beginnt auf einer neuen Seite. Das Inhaltsverzeichnis zeigt die erste H1-Überschrift, einen Link und die tatsächliche Startseite. Die Sortierung erfolgt nach Dateipfad. Nummerierte Dateinamen können die Reihenfolge festlegen.

## Bilder

- Bilder liegen im Repository und werden relativ zur jeweiligen Kapiteldatei aufgelöst, zum Beispiel `../bilder/prater4.jpg`.
- Auch Bildverweise in eingegebenem HTML werden verarbeitet.
- Fotos werden anhand ihres tatsächlichen Dateiformats geöffnet, korrekt gedreht und auf eine drucktaugliche Größe begrenzt.
- Alle verwendeten Fotos sind direkt in der HTML-Ausgabe eingebettet. Die heruntergeladene HTML-Datei benötigt keine Runner-Pfade oder zusätzlichen Bilddateien.
- Auskommentierte Bildplatzhalter werden nicht als aktive Bildverweise behandelt.
- Bei einem eindeutigen Pfad mit abweichender Groß-/Kleinschreibung wird das Bild eingebunden und ein Hinweis ausgegeben.
- Ein aktiver Verweis auf eine fehlende oder nicht lesbare Datei ergibt beim normalen Buchbau einen sichtbaren Bildhinweis. In der PR-Prüfung führt derselbe Fehler zu einer fehlgeschlagenen Prüfung.
- Noch nicht verlinkte Fotos werden nicht automatisch einem Text zugeordnet.

## Gemeinsamer Ablauf

`buch.yml` verwendet die Bauanleitung aus `reisefuehrer-pruefen.yml`. So nutzen PR-Vorschau und Hauptbranch dieselben Abhängigkeiten, Tests und Seiteneinstellungen. Der PDF-Satz erfolgt mit WeasyPrint; Chromium und Playwright werden nicht mehr benötigt.

Die GitHub-Actions-Zusammenfassung nennt alle aufgenommenen Kapitel und offenen Hinweise. Das Downloadpaket enthält `WienGuide.pdf`, die eigenständig nutzbare `WienGuide.html` und `Bauprotokoll.json`. Fehlgeschlagene Läufe können HTML und Protokoll zur Diagnose bereitstellen; sie enthalten kein altes PDF.

Generierte Dateien unter `ausgabe/` gehören nicht in die Versionsverwaltung. Sie werden bei jedem Lauf neu erzeugt und als Actions-Artefakt bereitgestellt.

## Lokal prüfen

Python 3.12 sowie die Pango-/Harfbuzz-Bibliotheken und Schriftarten aus dem Workflow werden benötigt.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python buch_erstellen.py --strict-images
```

Nur die eingebettete HTML-Ausgabe und das Protokoll erstellen:

```bash
python buch_erstellen.py --html-only
```

## Aktueller redaktioneller Stand

Die beiden Textdateien ohne Endung werden erkannt und mit einem Hinweis aufgenommen. Für die weitere Arbeit sollten sie die Endung `.md` erhalten. Doppelte Kapiteltitel und noch enthaltene Vorlagen-Platzhalter werden gemeldet. Schülertexte werden beim Bauen nicht gelöscht oder automatisch zusammengelegt.
