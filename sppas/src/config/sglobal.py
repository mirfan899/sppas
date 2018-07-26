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

    config.sglobal.py
    ~~~~~~~~~~~~~~~~~~

    Classes to manage global non-modifiable settings of SPPAS.

"""
from .settings import sppasBaseSettings

# ---------------------------------------------------------------------------


class sppasGlobalSettings(sppasBaseSettings):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Representation of global non-modifiable settings of SPPAS.

    """
    def __init__(self):
        sppasBaseSettings.__init__(self)
        self.__dict__ = dict(
            __version__="1.9.8",
            __author__="Brigitte Bigi",
            __contact__="brigite.bigi@gmail.com",
            __copyright__="Copyright (C) 2011-2018 Brigitte Bigi",
            __license__="GNU Public License, version 3",
            __docformat__='reStructedText en',
            __name__="SPPAS",
            __url__="http://www.sppas.org/",
            __summary__="SPPAS produces automatically annotations\n\
        from a recorded speech sound and its transcription\n\
        and performs the analysis of any annotated data.",
            __title__="the automatic annotation and analysis of speech",
            __encoding__="utf-8",
        )

# ---------------------------------------------------------------------------


class sppasPathsSettings(sppasBaseSettings):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Representation of global non-modifiable paths of SPPAS.

    """
    def __init__(self):
        sppasBaseSettings.__init__(self)
        self.__dict__ = dict(

        )

# ---------------------------------------------------------------------------
