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
from note import Note
	
class NoteEditor():
	
	def __init__(self, List, callback_method, combo):
		self.type_edit = gtk.glade.XML(GnomeConfig.main_gui, "edit_new")		
		self._init_alias()		
		self._init_signals()		
		self.fill_in_combobox(self.edit_combo, List)
		self.orgList = List		
		self.method = callback_method
		self.combobox = combo
	
	def _init_alias(self):
		self.editor 	= self.type_edit.get_widget("edit_new")
		self.title 		= self.type_edit.get_widget("edit_title")
		self.text 		= self.type_edit.get_widget("edit_text")
		self.edit_combo = self.type_edit.get_widget("edit_combobox")

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

	def _init_signals(self):
		SIGNAL_CONNECTIONS_DIC = {
			"on_cancel": self.cancel,
			"on_edit": self.edit,
            "on_new": self.new,
			"on_accept": self.accept,            
			"on_ok": self.ok,
        	}
		self.type_edit.signal_autoconnect(SIGNAL_CONNECTIONS_DIC)

	def cancel(self, widget):
		self.editor.destroy()

	def edit(self, widget):
		result = self.get_active(self.edit_combo)[1]
		self.title.set_text(result.get_title())
		self.text.set_text(result.get_text())
		self.current_title = result.get_title()

	def get_active(self, combobox):
		model = combobox.get_model()
		active = combobox.get_active()
		if active < 0:
			return None
		return model[active]

	def set_active(self, combobox):
		note = Note(self.title.get_text(), self.text.get_text())
		model = combobox.get_model()
		active = combobox.get_active()
		
		for medie in model:
			if medie[0] == self.current_title:
				medie[0] = self.title.get_text()
				medie[1].title 	= self.title.get_text()
				medie[1].text 	= self.text.get_text()

	def new(self, widget):
		title = self.title.get_text()
		if title != "":
			text = self.text.get_text()
			note = Note(title, text)
			model = self.edit_combo.get_model()
			model.append([title, note])

	def accept(self, widget):
		self.set_active(self.edit_combo)

	def get_items(self, combo):
		items = []
		for item in combo.get_model():
			items.append(item[1])
		return items

	def ok(self, widget):
		if (self.orgList != self.edit_combo.get_model()):
			items = self.get_items(self.edit_combo)
			print items
			self.method(self.combobox, items)
		self.editor.destroy()
