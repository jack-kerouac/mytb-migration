__author__ = 'florian'

import unittest
import datetime
import mytb


class MytbTest(unittest.TestCase):
    """Unit tests for mytb screen scraping."""

    def test_parse_entry_comments(self):
        """Test mytb parse_entry()."""

        entry = mytb.parse_entry('http://www.travelblog.org/Asia/Thailand/South-West-Thailand/Railay/blog-289162.html')

        self.assertEqual(len(entry.comments), 2)

        self.assertEqual(entry.comments[0].date, datetime.datetime(2008, 6, 19, 0, 0))
        self.assertEqual(entry.comments[0].author, 'Fritz')
        self.assertEqual(entry.comments[0].title, '')
        self.assertEqual(entry.comments[0].text,
                         'Hallo mein Sohn! Deine Bilder sind wirklich großartig und auch dein Kommentar klingt überzeugend. Natürlich sind Ma und ich froh, dass wir nicht alles, was du so getrieben hast, mitbekommen haben. Viel Spass dir noch und bleib jetzt auch mal auf dem Boden!')

        self.assertEqual(entry.comments[1].date, datetime.datetime(2008, 6, 22, 0, 0))
        self.assertEqual(entry.comments[1].author, 'Onkel W')
        self.assertEqual(entry.comments[1].title, 'Schade')
        self.assertEqual(entry.comments[1].text,
                         'Schade, dass man da nicht mit dem Wohnwagen hinfahren kann, Tina hat leider was gegens Fliegen. Tolle Fotos, sieht cool aus. Dummes Ding mit deiner Visa-Karte. \rMachs gut!\rO.W.')
