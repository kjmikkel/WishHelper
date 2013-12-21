# -*- coding: utf-8 -*-

#    This file is part of WishHelper.
#
#   WishHelper is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   WishHelper is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with The Lonely Runner Verifier.  If not, see <http://www.gnu.org/licenses/>.

#This is the gnome_frontend package. It's a GTK interface that want to be
#simple, HIG compliant and well integrated with Gnome.
import os
from enumerate import Enumerate

class GnomeConfig:

  current_rep = os.path.dirname(os.path.abspath(__file__))
  current_rep = os.path.join(current_rep, "gui")
  main_gui    = os.path.join(current_rep, "WishHelperMain.glade")
  helper_gui  = os.path.join(current_rep, "WishHelperEditor.glade")
#  edit_gui    = os.path.join(current_rep, "WishHelperEdit.glade")

  COL_NUMBER    = 0
  COL_TITLE     = 1
  COL_PRICE     = 2
  COL_TYPE      = 3
  COL_NOTE      = 4
