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

    src.annotations.annutils.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import shutil

from sppas.src.utils.fileutils import sppasFileUtils

# ------------------------------------------------------------------------


def fix_audioinput(inputaudioname):
    """Fix the audio file name that will be used.

    An only-ascii-based file name without whitespace is set if the
    current audio file name does not fit in these requirements.

    Notice that only the filename is checked, not the path.

    :param inputaudioname: (str) Audio file name

    """
    sf = sppasFileUtils(os.path.basename(inputaudioname))
    audio_file = sf.format()
    if audio_file != inputaudioname:
        shutil.copy(inputaudioname, audio_file)

    return audio_file

# ------------------------------------------------------------------------


def fix_workingdir(inputaudio=""):
    """Fix the working directory to store temporarily the data.

    :param inputaudio: (str) Audio file name

    """
    #if len(inputaudio) == 0:
        # Notice that the following generates a directory that the
        # aligners won't be able to access under Windows.
        # No problem with MacOS or Linux.
    sf = sppasFileUtils()
    workdir = sf.set_random()
    while os.path.exists(workdir) is True:
        workdir = sf.set_random()

    # else:
    #     audio_dir = os.path.dirname(inputaudio)
    #     sf = sppasFileUtils(audio_dir)
    #     formatted_audio_dir = sf.format()
    #     if audio_dir != formatted_audio_dir:
    #         raise IOError('No whitespace are allowed in the path of files')
    #
    #     workdir = audio_dir + "-temp"
    #     i = 1
    #     while os.path.exists(workdir) is True:
    #         workdir = audio_dir + "-temp" + str(i)
    #         i += 1

    audio_file = os.path.basename(inputaudio)
    sf = sppasFileUtils(audio_file)
    formatted_audio_file = sf.format()

    os.mkdir(workdir)
    shutil.copy(inputaudio, os.path.join(workdir, formatted_audio_file))

    return workdir
