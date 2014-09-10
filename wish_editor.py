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
#   along with WishHelper.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require('2.0')
import gobject
import gtk.glade
import os
import locale
import re
import datetime
import threading
import time
import sys
import pango

from __init__ import GnomeConfig
  
class WishEditor:

  def set_active_combo(self, combobox, break_value):
    model = combobox.get_model()
    for index in range(0, len(model)):
      combobox.set_active(index)
      ref = combobox.get_active_iter()
      val = model.get_value(ref, 0)
      if val == break_value:
        break

  def __init__(self, row):
    self._init_gui()
    self._init_signal_connections()
    self.old_row = row
    if row != []:
      self.name.set_text(row[0])
      self.price.set_value(row[1])
      self.slags.set_text(row[2])
      self.note.set_text(row[3])

  def run(self):
    return self.editor.run()
  
  def destroy(self):
    self.editor.destroy()

  def fill_in_combobox(self, combobox, List):
    store = gtk.ListStore(str, gobject.TYPE_PYOBJECT)
        
    for medie in List:      
      store.append([medie.get_title(), medie])
    
    combobox.set_model(store)
    cell = gtk.CellRendererText()
    combobox.pack_start(cell, True)
    combobox.add_attribute(cell, 'text',0)

    if len(List) > 0:  
      combobox.set_active(0)

  def _init_gui(self):
    self.builder = gtk.Builder()
    self.builder.add_from_file(GnomeConfig.helper_gui)
    self._init_alias()
    self.editor.set_title("Lav et Ønske")
    self.editor.set_icon_from_file("images/wishlist_add.png")
  
  def _init_alias(self):
    self.editor = self.builder.get_object("wish_editor")    
    self.name  = self.builder.get_object("wish_text")
    self.price = self.builder.get_object("price_spin")

    self.slags = self.builder.get_object("type_input")
    self.note = self.builder.get_object("note_input")
    

  def get_active_text(self, combobox):
    model = combobox.get_model()
    active = combobox.get_active()
    if active < 0:
      return None
    return model[active][0]

  def _init_signal_connections(self):
    SIGNAL_CONNECTIONS_DIC = { 
      "on_delete_cancel": lambda x: x.hide
        }
    self.builder.connect_signals(SIGNAL_CONNECTIONS_DIC)
