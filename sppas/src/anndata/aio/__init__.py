# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.aio.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Readers and writers of annotated data.

"""


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

ext_sppas = ['.xra', '.[Xx][Rr][Aa]']
ext_praat = ['.TextGrid', '.PitchTier', '.[Tt][eE][xX][tT][Gg][Rr][Ii][dD]','.[Pp][Ii][tT][cC][hH][Tt][Ii][Ee][rR]']
ext_transcriber = ['.trs','.[tT][rR][sS]']
ext_elan = ['.eaf', '[eE][aA][fF]']
ext_ascii = ['.txt','.csv', '.[cC][sS][vV]', '.[tT][xX][Tt]', '.info']
ext_phonedit = ['.mrk', '.[mM][rR][kK]']
ext_signaix = ['.hz', '.[Hh][zZ]']
ext_sclite = ['.stm', '.ctm', '.[sScC][tT][mM]']
ext_htk = ['.lab', '.mlf']
ext_subtitles = ['.sub', '.srt', '.[sS][uU][bB]', '.[sS][rR][tT]']
ext_anvil = ['.anvil', '.[aA][aN][vV][iI][lL]']
ext_annotationpro = ['.antx', '.[aA][aN][tT][xX]']
ext_xtrans = ['.tdf', '.[tT][dD][fF]']
ext_audacity = ['.aup']

extensions = ['.xra', '.textgrid', '.pitchtier', '.hz', '.eaf', '.trs', '.csv', '.mrk', '.txt', '.mrk', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', 'anvil', '.antx', '.tdf']
extensionsul = ext_sppas + ext_praat + ext_transcriber + ext_elan + ext_ascii + ext_phonedit + ext_signaix + ext_sclite + ext_htk + ext_subtitles + ext_anvil + ext_annotationpro + ext_xtrans + ext_audacity
extensions_in = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx', '.anvil', '.aup', '.trs', '.tdf', '.hz', '.PitchTier']
extensions_out = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx']
extensions_out_multitiers = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.antx', '.mlf']
