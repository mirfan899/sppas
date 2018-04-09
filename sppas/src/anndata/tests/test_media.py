# -*- coding:utf-8 -*-

import unittest

from ..media import sppasMedia

# ---------------------------------------------------------------------------


class TestMedia(unittest.TestCase):

    def setUp(self):
        pass

    def test_media_audio(self):
        m = sppasMedia("toto.wav")
        self.assertEqual(m.get_filename(), "toto.wav")
        self.assertEqual(m.get_mime_type(), "audio/wav")
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_video(self):
        m = sppasMedia("toto.mp4")
        self.assertEqual(m.get_filename(), "toto.mp4")
        self.assertEqual(m.get_mime_type(), "video/mp4")
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_mime_error(self):
        m = sppasMedia("toto.iii")
        self.assertEqual(m.get_filename(), "toto.iii")
        self.assertEqual(m.get_mime_type(), "audio/basic")
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_metadata(self):
        m = sppasMedia("toto.wav")
        m.set_meta("channel", "1")
        self.assertEqual(m.get_meta("channel"), "1")
        self.assertEqual(m.get_meta("canal"), "")
