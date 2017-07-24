#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import RESOURCES_PATH

from sppas.src.utils.makeunicode import u
from sppas.src.resources.vocab import sppasVocabulary
from sppas.src.resources.dictrepl import sppasDictRepl

from ..TextNorm.normalize import TextNormalizer
from ..TextNorm.transcription import sppasTranscription
from ..TextNorm.tokenize import sppasTokenizer

# ---------------------------------------------------------------------------


class TestNormalizer(unittest.TestCase):

    def setUp(self):
        dict_dir = os.path.join(RESOURCES_PATH, "vocab")
        vocab_file = os.path.join(dict_dir, "fra.vocab")
        punct_file = os.path.join(dict_dir, "Punctuations.txt")
        wds = sppasVocabulary(vocab_file)
        puncts = sppasVocabulary(punct_file)
        self.tok = TextNormalizer(wds, "fra")
        self.tok.set_punct(puncts)

    def test_clean_toe(self):

        t = sppasTranscription()

        s = t.clean_toe(u('(il) (ne) faut pas rêver'))
        self.assertEqual(s, u("faut pas rêver"))

        s = t.clean_toe(u('i(l) (ne) faut pas réver'))
        self.assertEqual(s, u("i(l) faut pas réver"))

        s = t.clean_toe(u('i(l) (ne) faut pas réver'))
        self.assertEqual(s, u("i(l) faut pas réver"))

        s = t.clean_toe(u(' (il) faut pas réver i(l)'))
        self.assertEqual(s, u("faut pas réver i(l)"))

        s = t.clean_toe(u(' euh [je sais, ché] pas '))
        self.assertEqual(s, u("euh [je_sais,ché] pas"))

        s = t.clean_toe(u("  j'[ avais,  avé ] "))
        self.assertEqual(s, u("j' [avais,avé]"))

        s = t.clean_toe(u("  [j(e) sais,  ché ] "))
        self.assertEqual(s, u("[je_sais,ché]"))

        s = t.clean_toe(u("  [peut-êt(re),  pe êt] "))
        self.assertEqual(s, u("[peut-être,peêt]"))

        s = t.clean_toe(u(" (pu)tai(n) j'ai"))
        self.assertEqual(s, u("(pu)tai(n) j'ai"))

        s = t.clean_toe(u("gpd_100y en a un  qu(i) est devenu complèt(e)ment  "))
        self.assertEqual(s, u("y en a un qu(i) est devenu complèt(e)ment"))

        s = t.clean_toe(u("[$Londre, T/$, Londreu]"))
        self.assertEqual(s, u("[Londre,Londreu]"))

        s = t.clean_toe(u("t(u) vois [$Isabelle,P /$, isabelleu] $Armelle,P /$ t(out) ça"))
        self.assertEqual(s, u("t(u) vois [Isabelle,isabelleu] Armelle t(out) ça"))

        s = t.clean_toe(u("gpd_1324ah euh"))
        self.assertEqual(s, u("ah euh"))

        s = t.clean_toe(u("ah a/b euh"))
        self.assertEqual(s, u("ah a/b euh"))

    def test_toe_spelling(self):

        t = sppasTranscription()
        s = t.toe_spelling(u('je, fais: "un essai".'))
        self.assertEqual(s, u('je , fais : " un essai " .'))

        s = t.toe_spelling(u('€&serie de punctuations!!!):-)".'))
        self.assertEqual(s, u('€ & serie de punctuations ! ! ! ) : - ) " .'))

        s = t.toe_spelling(u('123,2...'))
        self.assertEqual(s, u('123,2 . . .'))

        # this is sampa to be sent directly to the phonetizer
        s = t.toe_spelling(u(" /l-e-f-o~-n/ "))
        self.assertEqual(s, u('/l-e-f-o~-n/'))

        # this is not sampa, because sampa can't contain whitespace.
        s = t.toe_spelling(u('/le mot/'))
        self.assertEqual(s, u('/ le mot /'))

        s = t.toe_spelling(u('(/'))
        self.assertEqual(s, u('( / '))

    def test_toe(self):

        t = sppasTranscription()
        s = t.clean_toe(u(" /l-e-f-o~-n/ "))
        s = t.toe_spelling(s)
        self.assertEqual(s, u('/l-e-f-o~-n/'))

        s = t.clean_toe(u(" /le mot/ "))
        s = t.toe_spelling(s)
        self.assertEqual(s, u('/ le mot /'))

    def test_replace(self):

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace([u("un"), u("taux"), u("de"), u("croissance"), u("de"), u("0,5"), u("%")])
        self.assertEquals(s, [u("un"), u("taux"), u("de"), u("croissance"), u("de"), u("0"), u("virgule"), u("5"),
                              u("pourcents")])

        text = [u("² % °c  km/h  etc   €  ¥ $ ")]

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "eng.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u("square percent degrees_Celsius km/h etc euros yens dollars"))

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "spa.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u("quadrados por_ciento grados_Celsius km/h etc euros yens dollars"))

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s),
                          u("carrés pourcents degrés_celcius kilomètres_heure etcetera euros yens dollars"))

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "ita.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u("quadrato percento gradi_Celsius km/h etc euros yens dollars"))

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "cmn.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u("的平方 个百分比 摄氏度 公里每小时 etc € ¥ $"))

    def test_tokenize(self):

        self.tok.set_lang("fra")
        splitfra = self.tok.tokenize(u("l'assiette l'abat-jour paris-brest et paris-marseille").split())
        self.assertEqual(splitfra, u("l' assiette l' abat-jour paris-brest et paris - marseille").split())

        s = self.tok.normalize(u("ah a/b euh"))
        self.assertEqual(s, u("ah a/b euh"))

        # sampa
        s = self.tok.normalize(u("/l-e-f-o~-n/"))
        self.assertEqual(s, u('/l-e-f-o~-n/'))

        # not sampa...
        s = self.tok.normalize(u("/le mot/"))
        self.assertEqual(s, u('le mot'))

    def test_num2letter(self):
        """ Test the integration of num2letter into the TextNormalizer. """

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        self.tok.set_lang("fra")

        s = self.tok.normalize(u("123"))
        self.assertEquals(s, u("cent-vingt-trois"))

        s = self.tok.normalize(u("1,24"))
        self.assertEquals(s, u("un virgule vingt-quatre"))

        self.tok.set_lang("cat")
        with self.assertRaises(ValueError):
            self.tok.normalize(u("123"))

    def test_remove_punct(self):

        self.tok.set_lang("fra")
        s = self.tok.normalize(u("/un, deux!!!"))
        self.assertEquals(s, u("un deux"))

    def test_stick(self):

        t = sppasTokenizer(self.tok.vocab)
        s = t.bind([u("123")])
        self.assertEquals(s, [u("123")])
        s = t.bind([u("au fur et à mesure")])
        self.assertEquals(s, [u("au_fur_et_à_mesure")])
        s = t.bind([u("rock'n roll")])   # not in lexicon
        self.assertEquals(s, [u("rock'n")])

    def test_sampa(self):

        repl = sppasDictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)

        s = self.tok.normalize(u("[le mot,/lemot/]"), [])
        self.assertEqual(u("/lemot/"), s)
        s = self.tok.normalize(u("[le mot,/lemot/]"), ["std"])
        self.assertEqual(u("le_mot"), s)
        s = self.tok.normalize(u("[le mot,/lemot/]"))
        self.assertEqual(u("/lemot/"), s)

        # minus is accepted in sampa transcription (it is the phonemes separator)
        s = self.tok.normalize(u(" /l-e-f-o~-n/ "))
        self.assertEqual(u("/l-e-f-o~-n/"), s)

        s = self.tok.normalize(u(" /le~/ "))
        self.assertEqual(u("/le~/"), s)

        # whitespace is not accepted in sampa transcription
        s = self.tok.normalize(u(" /le mot/ "))
        self.assertEqual(u("le mot"), s)

        t = sppasTranscription()
        s = t.clean_toe(u("ah a/b euh"))
        self.assertEqual(s, u("ah a/b euh"))

    def test_code_switching(self):

        dictdir  = os.path.join(RESOURCES_PATH, "vocab")
        vocabfra = os.path.join(dictdir, "fra.vocab")
        vocabcmn = os.path.join(dictdir, "cmn.vocab")

        wds = sppasVocabulary(vocabfra)
        wds.load_from_ascii(vocabcmn)
        self.assertEquals(len(wds), 457922)

        #self.tok.set_vocab(wds)
        #splitswitch = self.tok.tokenize(u'et il m\'a dit : "《干脆就把那部蒙人的闲法给废了拉倒！》RT @laoshipukong : 27日"')
        #self.assertEqual(splitswitch, u"et il m' a dit 干脆 就 把 那 部 蒙 人 的 闲 法 给 废 了 拉倒 rt @ laoshipukong 二十七 日")

    def test_acronyms(self):

        self.tok.set_lang("fra")
        print(self.tok.normalize(""))
