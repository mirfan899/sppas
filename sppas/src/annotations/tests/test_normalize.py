#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import RESOURCES_PATH
from sppas.src.resources.vocab import Vocabulary
from sppas.src.resources.dictrepl import DictRepl

from ..TextNorm.tokenize import TextNormalizer, sppasTranscription, sppasTokenizer

# ---------------------------------------------------------------------------


class TestDictTok(unittest.TestCase):

    def setUp(self):
        dictdir = os.path.join(RESOURCES_PATH, "vocab")
        vocabfile = os.path.join(dictdir, "fra.vocab")
        wds = Vocabulary(vocabfile)
        self.tok = TextNormalizer(wds, "fra")

    def test_num2letter(self):
        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        self.tok.set_lang("fra")

        s = self.tok.normalize(u"123")
        self.assertEquals(s, u"cent-vingt-trois")

        s =  self.tok.normalize(u"1,24")
        self.assertEquals(s, u"un virgule vingt-quatre")

    def test_stick(self):
        t = sppasTokenizer(self.tok.vocab)
        s = t.bind([u"123"])
        self.assertEquals(s, [u"123"])
        s = t.bind([u"au fur et à mesure"])
        self.assertEquals(s, [u"au_fur_et_à_mesure"])
        s = t.bind([u"rock'n roll"])   # not in lexicon
        self.assertEquals(s, [u"rock'n"])

    def test_replace(self):
        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace([u"un", u"taux", u"de", u"croissance", u"de", u"0,5", u"%"])
        self.assertEquals(s, [u"un", u"taux", u"de", u"croissance", u"de", u"0", u"virgule", u"5", u"pourcents"])

        text = [u"² % °c  km/h  etc   €  ¥ $ "]

        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "eng.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u"square percent degrees_Celsius km/h etc euros yens dollars")

        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "spa.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u"quadrados por_ciento grados_Celsius km/h etc euros yens dollars")

        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u"carrés pourcents degrés_celcius kilomètres_heure etcetera euros yens dollars")

        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "ita.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u"quadrato percento gradi_Celsius km/h etc euros yens dollars")

        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "cmn.repl"), nodump=True)
        self.tok.set_repl(repl)
        s = self.tok.replace(text)
        self.assertEquals(" ".join(s), u"的平方 个百分比 摄氏度 公里每小时 etc € ¥ $")

    def test_clean_toe(self):
        t = sppasTranscription()
        s = t.clean_toe(u'(il) (ne) faut pas rêver')
        self.assertEqual(s, u"faut pas rêver")

        s = t.clean_toe(u'i(l) (ne) faut pas réver')
        self.assertEqual(s, u"i(l) faut pas réver")

        s = t.clean_toe(u'i(l) (ne) faut pas réver')
        self.assertEqual(s, u"i(l) faut pas réver")

        s = t.clean_toe(u' (il) faut pas réver i(l)')
        self.assertEqual(s, u"faut pas réver i(l)")

        s = t.clean_toe(u' euh [je sais, ché] pas ')
        self.assertEqual(s, u"euh [je_sais,ché] pas")

        s = t.clean_toe(u"  j'[ avais,  avé ] ")
        self.assertEqual(s, u"j' [avais,avé]")

        s = t.clean_toe(u"  [j(e) sais,  ché ] ")
        self.assertEqual(s, u"[je_sais,ché]")

        s = t.clean_toe(u"  [peut-êt(re),  pe êt] ")
        self.assertEqual(s, u"[peut-être,peêt]")

        s = t.clean_toe(u" (pu)tai(n) j'ai")
        self.assertEqual(s, u"(pu)tai(n) j'ai")

        s = t.clean_toe(u"gpd_100y en a un  qu(i) est devenu complèt(e)ment  ")
        self.assertEqual(s, u"y en a un qu(i) est devenu complèt(e)ment")

        s = t.clean_toe(u"[$Londre, T/$, Londreu]")
        self.assertEqual(s, u"[Londre,Londreu]")

        s = t.clean_toe(u"t(u) vois [$Isabelle,P /$, isabelleu] $Armelle,P /$ t(out) ça")
        self.assertEqual(s, u"t(u) vois [Isabelle,isabelleu] Armelle t(out) ça")

        s = t.clean_toe(u"gpd_1324ah euh")
        self.assertEqual(s, u"ah euh")

        s = t.clean_toe(u"ah a/b euh")
        self.assertEqual(s, u"ah a/b euh")

    def test_sampa(self):
        repl = DictRepl(os.path.join(RESOURCES_PATH, "repl", "fra.repl"), nodump=True)
        self.tok.set_repl(repl)

        s = self.tok.normalize(u"[le mot,/lemot/]", [])
        self.assertEqual(u"/lemot/", s)
        s = self.tok.normalize(u"[le mot,/lemot/]", ["std"])
        self.assertEqual(u"le_mot", s)

        t = sppasTranscription()
        s = t.clean_toe(u"ah a/b euh")
        self.assertEqual(s, u"ah a/b euh")

    def test_tokenize(self):
        self.tok.set_lang("fra")
        splitfra = self.tok.tokenize(u"l'assiette l'abat-jour et le paris-brest et paris-marseille".split())
        self.assertEqual(splitfra, u"l' assiette l' abat-jour et le paris-brest et paris - marseille".split())

        s = self.tok.normalize(u"ah a/b euh")
        self.assertEqual(s, u"ah a/b euh")

    def test_code_switching(self):
        dictdir  = os.path.join(RESOURCES_PATH, "vocab")
        vocabfra = os.path.join(dictdir, "fra.vocab")
        vocabcmn = os.path.join(dictdir, "cmn.vocab")

        wds = Vocabulary(vocabfra)
        wds.load_from_ascii(vocabcmn)
        self.assertEquals(wds.get_size(), 457933)

        #self.tok.set_vocab(wds)
        #splitswitch = self.tok.tokenize(u'et il m\'a dit : "《干脆就把那部蒙人的闲法给废了拉倒！》RT @laoshipukong : 27日"')
        #self.assertEqual(splitswitch, u"et il m' a dit 干脆 就 把 那 部 蒙 人 的 闲 法 给 废 了 拉倒 rt @ laoshipukong 二十七 日")
