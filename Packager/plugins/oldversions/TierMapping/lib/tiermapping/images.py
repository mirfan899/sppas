# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of TierMapping.
#
# TierMapping is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TierMapping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TierMapping.  If not, see <http://www.gnu.org/licenses/>.

import os

_path = os.path.join(
        os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))),"icons")


IMG_EXIT   = os.path.join(_path, "logout.png")
IMG_ADD    = os.path.join(_path, "list-add.png")
IMG_REMOVE = os.path.join(_path, "list-remove.png")
IMG_CLEAR  = os.path.join(_path, "list-clear.png")
IMG_SAVE   = os.path.join(_path, "save.png")
IMG_EXCEL  = os.path.join(_path, "excel-icon.png")
IMG_FIND  = os.path.join(_path, "find-and-replace.png")
IMG_ABOUT = os.path.join(_path, "about.png")
