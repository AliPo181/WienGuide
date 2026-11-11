import base64
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from buch_erstellen import Buch, bauen


class BuchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'kapitel').mkdir()
        (self.root / 'bilder').mkdir()
        self.kapitel = self.root / 'kapitel' / 'gruppe.md'
        (self.root / 'deckblatt.md').write_text('# Testbuch', encoding='utf-8')
        (self.root / 'buch.css').write_text('@page { size: A4; }', encoding='utf-8')
        Image.new('RGB', (20, 10), 'blue').save(self.root / 'bilder' / 'Grüner Park.jpg')

    def test_relative_und_root_pfade_werden_eingebettet(self):
        self.kapitel.write_text('# Park\n\n![Foto](../bilder/Gr%C3%BCner%20Park.jpg)\n\n'
                                '![Foto](bilder/Gr%C3%BCner%20Park.jpg)', encoding='utf-8')
        buch = Buch(self.root)
        titel, html = buch.render(self.kapitel, 'k1')
        self.assertEqual(titel, 'Park')
        self.assertEqual(buch.bilder, 2)
        self.assertEqual(html.count('data:image/jpeg;base64,'), 2)
        self.assertNotIn('file://', html)

    def test_html_bilder_und_auskommentierte_platzhalter(self):
        self.kapitel.write_text('# Park\n\n<img src="../bilder/Grüner Park.jpg">\n\n'
                                '<!-- ![Platzhalter](fehlt.jpg) -->', encoding='utf-8')
        buch = Buch(self.root)
        _, html = buch.render(self.kapitel, 'k1')
        self.assertEqual(buch.bilder, 1)
        self.assertEqual(buch.bildfehler, [])
        self.assertNotIn('fehlt.jpg', html)

    def test_fehlendes_bild_liefert_hinweis_statt_abbruch(self):
        self.kapitel.write_text('# Park\n\n![Aussicht](fehlt.jpg)', encoding='utf-8')
        bericht = bauen(self.root, nur_html=True)
        self.assertEqual(len(bericht['bildfehler']), 1)
        html = (self.root / 'ausgabe/WienGuide.html').read_text()
        self.assertIn('Bild noch nicht verfügbar: Aussicht', html)
        self.assertNotIn('<img', html)

    def test_strenge_pr_pruefung_blockiert_fehlende_bilder(self):
        self.kapitel.write_text('# Park\n\n![Foto](fehlt.jpg)', encoding='utf-8')
        out = self.root / 'ausgabe'
        out.mkdir()
        (out / 'WienGuide.pdf').write_bytes(b'alter Stand')
        with self.assertRaises(ValueError):
            bauen(self.root, strict=True, nur_html=True)
        self.assertFalse((out / 'WienGuide.pdf').exists())
        self.assertEqual(len(json.loads((out / 'Bauprotokoll.json').read_text())['bildfehler']), 1)

    def test_endungslose_kapitel_werden_nicht_verschluckt(self):
        self.kapitel.write_text('# Park', encoding='utf-8')
        (self.root / 'kapitel/ohne-endung').write_text('# Ein weiteres Kapitel', encoding='utf-8')
        (self.root / 'kapitel/.gitkeep').touch()
        (self.root / 'kapitel/kein-kapitel').write_bytes(b'\x00\xff')
        self.assertEqual(len(Buch(self.root).kapiteldateien()), 2)

    def test_titel_aus_markdown_statt_codeblock_und_eindeutige_links(self):
        self.kapitel.write_text('```\n# Nicht der Titel\n```\n\n# **Park** & Garten\n\n'
                                '[Zum Garten](#garten)\n\n## Garten', encoding='utf-8')
        titel, html = Buch(self.root).render(self.kapitel, 'k7')
        self.assertEqual(titel, 'Park & Garten')
        self.assertIn('id="k7-garten"', html)
        self.assertIn('href="#k7-garten"', html)

    def test_eindeutige_grossschreibung_wird_mit_hinweis_korrigiert(self):
        self.kapitel.write_text('# Park\n\n![Foto](../bilder/grüner%20park.JPG)', encoding='utf-8')
        buch = Buch(self.root)
        buch.render(self.kapitel, 'k1')
        self.assertEqual(buch.bilder, 1)
        self.assertEqual(buch.bildfehler, [])
        self.assertTrue(any('Groß-/Kleinschreibung' in x for x in buch.hinweise))

    def test_bildgroesse_wird_begrenzt(self):
        Image.new('RGB', (5000, 100), 'red').save(self.root / 'bilder/gross.jpg')
        data = Buch(self.root).bild('../bilder/gross.jpg', self.kapitel)
        with Image.open(io.BytesIO(base64.b64decode(data.split(',', 1)[1]))) as bild:
            self.assertLessEqual(bild.width, 2400)
            self.assertGreater(bild.height, 0)


if __name__ == '__main__':
    unittest.main()
