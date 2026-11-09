WienGuide
Ein gemeinsamer Wien-Reiseführer aus einem Git- und GitHub-Workshop.

In diesem Projekt erstellen Schülerinnen und Schüler in Zweiergruppen ein gemeinsames Buch über Wien. Jede Gruppe wählt ihr Thema, ihre Orte und ihren Kapiteltitel selbst und gestaltet ihren Beitrag mit Texten und Bildern.

Dabei lernen die Teilnehmenden den praktischen Ablauf der Versionsverwaltung kennen: ein Repository klonen, auf einem eigenen Branch arbeiten, Änderungen mit Commits dokumentieren, auf GitHub hochladen und über einen Pull Request zusammenführen.

Aus den angenommenen Beiträgen entsteht automatisch ein PDF-Reiseführer mit Deckblatt und Inhaltsverzeichnis. Die Kapitel liegen als Markdown-Dateien vor; die PDF-Erstellung läuft über GitHub Actions.
Das fertige Buch herunterladen
1. Oben im Repository auf Actions klicken.
2. Den neuesten erfolgreichen Durchlauf von Reiseführer erstellen öffnen. Er ist mit einem grünen Häkchen gekennzeichnet.
3. Unter Artifacts das Paket WienGuide herunterladen. Dafür ist eine GitHub-Anmeldung erforderlich.
4. Die ZIP-Datei entpacken und WienGuide.pdf öffnen.
Nach Änderungen auf main wird das PDF neu erstellt. Die Downloads der einzelnen Durchläufe stehen jeweils 30 Tage bereit.
Aufbau des Projekts
Datei oder Ordner	Inhalt
deckblatt.md	Bindet das Titelbild des Reiseführers ein
kapitel/	Kapiteldateien der Gruppen
bilder/	Titelbild und eigene Unterordner für die Bilder jeder Gruppe
buch.css	Gestaltung von Deckblatt, Inhaltsverzeichnis und Kapiteln
buch_erstellen.py	Fügt die Inhalte zusammen und erzeugt das PDF
requirements.txt	Benötigte Python-Pakete für die Bucherstellung
.github/workflows/buch.yml	Automatische PDF-Erstellung auf GitHub


So tragt ihr zum Reiseführer bei
Die folgenden Namen gelten als Beispiel für Gruppe 1. Passt die Gruppennummer in Branch, Dateiname und Bildpfaden an eure Gruppe an.
1. Erstellt euren Branch, zum Beispiel gruppe-1.
2. Erstellt in VS Code die Datei kapitel/gruppe-1.md und kopiert die Vorlage unten hinein.
3. Wählt selbst einen Kapiteltitel und ersetzt die Platzhalter durch eure Inhalte. Die erste Überschrift mit # wird als Kapitelname im Inhaltsverzeichnis übernommen.
4. Speichert eure Bilder im Ordner bilder/gruppe-1/ und passt die Bildverweise an.
5. Speichert eure Dateien, erstellt Commits und ladet euren Branch mit git push hoch.
6. Öffnet einen Pull Request mit base: main und compare: eurem Gruppenbranch. Die Workshop-Leitung prüft die Beiträge und führt sie zusammen.
Bearbeitet auf eurem Gruppenbranch eure eigene Kapiteldatei und euren eigenen Bilderordner. Titel, Inhalt und Gliederung dürft ihr frei gestalten: Die folgende Vorlage ist eine Hilfe und kann angepasst werden.
Kopiervorlage für euer Kapitel
Kopiert den Inhalt des folgenden Codeblocks in eure Kapiteldatei. Die äußeren Begrenzungen des Codeblocks gehören nicht in die Datei.
# [Euer selbst gewählter Kapiteltitel]

*Ein Beitrag von [euren Namen oder eurem Gruppennamen]*

[Schreibt eine kurze Einleitung: Worum geht es in eurem Kapitel?
Was möchtet ihr Leserinnen und Lesern über Wien zeigen?]

## [Eure erste Zwischenüberschrift]

[Hier beginnt euer Text. Beschreibt eure ausgewählten Orte,
Erlebnisse oder Besonderheiten.]

> **Bildplatzhalter 1:** Hier soll euer erstes Foto erscheinen.

<!-- Erst aktivieren, wenn die Bilddatei vorhanden ist:
![Beschreibung eures ersten Fotos](../bilder/gruppe-1/foto-1.jpg)
-->

*[Bildunterschrift sowie Bildquelle, Urheber und gegebenenfalls Lizenz]*

## [Eure nächste Zwischenüberschrift]

[Hier könnt ihr weitere Inhalte ergänzen.]

> **Bildplatzhalter 2:** Hier soll euer zweites Foto erscheinen.

<!-- Erst aktivieren, wenn die Bilddatei vorhanden ist:
![Beschreibung eures zweiten Fotos](../bilder/gruppe-1/foto-2.jpg)
-->

*[Bildunterschrift sowie Bildquelle, Urheber und gegebenenfalls Lizenz]*

## Unser Tipp

[Was würdet ihr anderen für einen Besuch empfehlen?]

## Quellen

- [Titel eurer Quelle](https://example.org)

*Stand unserer Recherche: [Datum]*
So ersetzt ihr die Bildplatzhalter
1. Legt im Projektordner bilder euren Unterordner an, zum Beispiel gruppe-1.
2. Kopiert eure Fotos dort hinein, beispielsweise als foto-1.jpg und foto-2.jpg. Verwendet einfache Dateinamen ohne Leerzeichen und achtet auf die tatsächliche Dateiendung.
3. Passt die Bildpfade in eurer Kapiteldatei an. Groß- und Kleinschreibung müssen mit den Dateinamen übereinstimmen.
4. Entfernt vor und nach dem jeweiligen Bildverweis die Kommentarzeilen <!-- ... und -->. Danach steht der Bildverweis allein im Text, zum Beispiel:
   ![Blick auf unseren ausgewählten Ort](../bilder/gruppe-1/foto-1.jpg)
5. Löscht den zugehörigen Absatz Bildplatzhalter und ergänzt Bildbeschreibung, Bildunterschrift und Quelle.
6. Prüft das Ergebnis in der Markdown-Vorschau von VS Code: Strg + K, danach V.
Die Bildverweise in der Vorlage sind zunächst auskommentiert, damit die PDF-Erstellung auch ohne hochgeladene Fotos funktioniert. Wenn ihr ein Bild nicht benötigt, entfernt den gesamten zugehörigen Platzhalterblock. Verwendet eigene oder passend lizenzierte Bilder und nennt die erforderlichen Quellenangaben.
Vor dem Pull Request prüfen
- Liegt eure Kapiteldatei im Ordner kapitel und endet ihr Name auf .md?
- Habt ihr die Platzhalter ersetzt oder entfernt?
- Werden die Bilder in der Vorschau angezeigt und sind ihre Dateien mit im Commit enthalten?
- Sind eure Quellen angegeben und alle Dateien gespeichert?
- Habt ihr eure letzten Änderungen committed und auf euren Gruppenbranch gepusht?
Nach dem Zusammenführen erstellt GitHub den aktualisierten Reiseführer. Die Kapitel werden alphabetisch nach Dateiname angeordnet.
