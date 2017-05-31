# -*- coding:utf-8 -*-

import unittest

from ..infotheory.entropy import Entropy
from ..infotheory.kullbackleibler import KullbackLeibler
from ..infotheory.perplexity import Perplexity

# ---------------------------------------------------------------------------


class TestInformationTheory(unittest.TestCase):

    def test_entropy(self):
        entropy = Entropy(list("1223334444"))

        self.assertEqual(round(entropy.eval(), 5), 1.84644)
        entropy.set_symbols(list("0000000000"))
        self.assertEqual(round(entropy.eval(), 5), 0.)
        entropy.set_symbols(list("1000000000"))
        self.assertEqual(round(entropy.eval(), 5), 0.469)
        entropy.set_symbols(list("1100000000"))
        self.assertEqual(round(entropy.eval(), 5), 0.72193)
        entropy.set_symbols(list("1110000000"))
        self.assertEqual(round(entropy.eval(), 5), 0.88129)
        entropy.set_symbols(list("1111000000"))
        self.assertEqual(round(entropy.eval(), 5), 0.97095)
        entropy.set_symbols(list("1111100000"))
        self.assertEqual(round(entropy.eval(), 5), 1.)
        entropy.set_symbols(list("1111111111"))
        self.assertEqual(round(entropy.eval(), 5), 0.)
        entropy.set_symbols(list("1111000000"))
        entropy.set_ngram(1)
        self.assertEqual(round(entropy.eval(), 5), 0.97095)
        entropy.set_ngram(2)
        self.assertEqual(round(entropy.eval(), 5), 1.35164)
        entropy.set_symbols(list("1010101010"))
        self.assertEqual(round(entropy.eval(), 5), 0.99108)
        entropy.set_symbols(list("1111100000"))
        self.assertEqual(round(entropy.eval(), 5), 1.39215)

    def test_perplexity(self):
        model = dict()
        model["peer"] = 0.1
        model["pineapple"] = 0.2
        model["tomato"] = 0.3
        model["apple"] = 0.4
        pp = Perplexity(model)
        observed = ['apple', 'pineapple', 'apple', 'peer']
        self.assertEqual(round(pp.eval_pp(observed), 5), 3.61531)
        observed = ['apple', 'pineapple', 'apple', 'tomato']
        self.assertEqual(round(pp.eval_pp(observed), 5), 4.12107)
        observed = ['apple', 'grapefruit', 'apple', 'peer']
        self.assertEqual(round(pp.eval_pp(observed), 5), 2.62034)

    def test_kl1(self):
        data = list('00000011000101010000100101000101000001000100000001100000')
        kl = KullbackLeibler()
        kl.set_epsilon(1.0 / (10.*len(data)))
        kl.set_model_from_data(data)
        kl.set_observations(list('000'))
        self.assertEqual(round(kl.eval_kld(), 5), 1796.01074)
        kl.set_observations(list('010'))
        self.assertEqual(round(kl.eval_kld(), 5), 1120.27006)
        kl.set_observations(list('011'))
        self.assertEqual(round(kl.eval_kld(), 5), 1120.27006)
        kl.set_observations(list('111'))
        self.assertEqual(round(kl.eval_kld(), 5), 1796.01074)

    def test_kl2(self):
        modell = dict()
        modell["a"] = 0.80
        modell["b"] = 0.08
        modell["c"] = 0.08
        modell["d"] = 0.04
        kll = KullbackLeibler(modell)
        kll.set_epsilon(1. / 1000.)
        observation = list()
        observation.append("a")
        observation.append("a")
        kll.set_observations(observation)
        self.assertEqual(round(kll.eval_kld(), 5), 1.33276)
        observation.pop(0)
        observation.append("b")
        self.assertEqual(round(kll.eval_kld(), 5), 2.01852)
        observation.pop(0)
        observation.append("d")
        self.assertEqual(round(kll.eval_kld(), 5), 10.98264)

        model = dict()
        model[(0, 0)] = 0.80
        model[(0, 1)] = 0.08
        model[(1, 0)] = 0.08
        model[(1, 1)] = 0.04
        kl = KullbackLeibler(model)
        kl.set_epsilon(1. / 1000.)
        observation = list()
        observation.append((0, 0))
        observation.append((0, 0))
        kl.set_observations(observation)
        self.assertEqual(round(kl.eval_kld(), 5), 1.33276)
        observation.pop(0)
        observation.append((0, 1))
        self.assertEqual(round(kl.eval_kld(), 5), 2.01852)
        observation.pop(0)
        observation.append((1, 1))
        self.assertEqual(round(kl.eval_kld(), 5), 10.98264)
