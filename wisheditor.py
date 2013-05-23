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
from edit_note import NoteEditor
	
class WishEditor :

	def set_active_combo(self, combobox, break_value):
		model = combobox.get_model()
		for index in range(0, len(model) - 1):
			combobox.set_active(index)
			ref = combobox.get_active_iter()
			val = model.get_value(ref, 0)
			if val == break_value:
				break

	def __init__(self, row, response, Slags = None, Notes = None):
		self._init_gui(Slags, Notes)
		self._init_signal_connections()
		self.response = response
		self.old_row = row
		if row != []:
			self.name.set_text(row[0])
			self.price.set_value(row[1])
			self.set_active_combo(self.slags, row[2].get_title())
			self.set_active_combo(self.notes, row[3].get_title())

	def set_combo_store(self, combobox, List):
		store = gtk.ListStore(str, gobject.TYPE_PYOBJECT)		
		for medie in List:
			store.append([medie.get_title(), medie])
		
		combobox.set_model(store)
		if len(List) > 0:	
			combobox.set_active(0)


	def fill_in_combobox(self, combobox, List):		
		self.set_combo_store(combobox, List)

		cell = gtk.CellRendererText()
		combobox.pack_start(cell, True)
  		combobox.add_attribute(cell, 'text',0)

	def _init_gui(self, Slags, Notes):
		self.gui = gtk.glade.XML(GnomeConfig.main_gui, "wish_editor")		
		self._init_alias()
		
		if Slags == None:
			Slags = GnomeConfig.start_media

		if Notes == None:
			Notes = GnomeConfig.start_notes

		self.Slags = Slags
		self.Notes = Notes		
		
		print "Slags:", self.Slags
		print "Notes:", self.Notes
		
		self.fill_in_combobox(self.slags, Slags)
		self.fill_in_combobox(self.notes, Notes)
	

	def _init_alias(self):
		self.editor = self.gui.get_widget("wish_editor")		
		self.name  = self.gui.get_widget("wish_text")
		self.price = self.gui.get_widget("price_spin")
		self.slags = self.gui.get_widget("type_combo")
		self.notes = self.gui.get_widget("note_combo")
		
	def get_active_text(self, combobox):
		model = combobox.get_model()
		active = combobox.get_active()
		if active < 0:
			return None
		return model[active][0]

	def get_selected_combo(self, combobox):
		combo_model = combobox.get_model()
		combo_active = combobox.get_active_iter()
		if combo_active != None:
			return combo_model.get_value(combo_active, 1)
		else:
			return None

	def response(self, widget):
		
		name = self.name.get_text()
		price = self.price.get_value()		

		slags = self.get_selected_combo(self.slags)
		note = self.get_selected_combo(self.notes)
		
		if self.old_row != []:
			print self.old_row			
			old_slags = self.old_row[2]
			if old_slags.get_sid() != slags.get_sid():
				old_slags.remove_wish()
				slags.add_wish()
		
			old_note = self.old_row[3]
			if old_note.get_nid() != note.get_nid():
				old_note.remove_wish()
				note.add_wish()
			print old_slags
			print old_note	 
		else:
			slags.add_wish()
			note.add_wish()		

		self.response([name, price, slags.title, note.title, slags, note])					
		self.editor.destroy()		
		
  	def cancel(self, widget):
		self.editor.destroy()

  	def new_note(self, widget):
		self.edit_new(self.Notes, self.notes)

	def remove_note(self, widget):
		self.delete_row(self.notes)

	def delete_row(self, combobox):
		combo_value = self.get_selected_combo(combobox)
		title = combo_value.get_title() 
		if combo_value != None and combo_value.can_delete() and (title != "Ingen" and not (title in GnomeConfig.start_media_txt)):
			combo_active = combobox.get_active()
			combobox.remove_text(combo_active)
			if len(combobox.get_model()) > 0:
				combobox.set_active(0)

	def edit_new(self, List, combobox):
		note = NoteEditor(List, self.set_combo_store, combobox)
				
	def new_type(self, widget):
		self.edit_new(self.Slags, self.slags)
		
	def remove_type(self, widget):
		self.delete_row(self.slags)

  	def _init_signal_connections(self):
		SIGNAL_CONNECTIONS_DIC = {
			"on_cancel": self.cancel,
			"on_response": self.response,
            "on_new_note": self.new_note,
			"on_remove_note": self.remove_note,            
			"on_new_slags": self.new_type,
			"on_remove_slags": self.remove_type,
			"on_delete_cancel": lambda x: x.hide
        	}
		self.gui.signal_autoconnect(SIGNAL_CONNECTIONS_DIC)
