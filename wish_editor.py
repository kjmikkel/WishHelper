# -*- coding: utf-8 -*-
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
from note_editor import NoteEditor
from note import Note

	
class WishEditor:

	def set_active_combo(self, combobox, break_value):
		model = combobox.get_model()
		for index in range(0, len(model) - 1):
			combobox.set_active(index)
			ref = combobox.get_active_iter()
			val = model.get_value(ref, 0)
			if val == break_value:
				break

	def __init__(self, row, Slags = None, Notes = None):
		self._init_gui(Slags, Notes)
		self._init_signal_connections()
		self.old_row = row
		if row != []:
			self.name.set_text(row[0])
			self.price.set_value(row[1])
			self.set_active_combo(self.slags, row[2].get_title())
			self.set_active_combo(self.notes, row[3].get_title())

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

	def _init_gui(self, Slags, Notes):
		self.builder = gtk.Builder()
		self.builder.add_from_file(GnomeConfig.helper_gui)
		self._init_alias()
		
		self.Slags = Slags
		self.Notes = Notes		
				
		self.fill_in_combobox(self.slags, Slags)
		self.fill_in_combobox(self.notes, Notes)
	
	def _init_alias(self):
		self.editor = self.builder.get_object("wish_editor")		
		self.name  = self.builder.get_object("wish_text")
		self.price = self.builder.get_object("price_spin")
		self.slags = self.builder.get_object("type_combo")
		self.notes = self.builder.get_object("note_combo")
		
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
			return No

	def delete_row(self, combobox):
		combo_value = self.get_selected_combo(combobox)
		title = combo_value.get_title() 
		if combo_value != None and combo_value.can_delete() and (title != "Ingen" and not (title in GnomeConfig.start_media_txt)):
			combo_active = combobox.get_active()
			combobox.remove_text(combo_active)
			if len(combobox.get_model()) > 0:
				combobox.set_active(0)

		# Types
	def new_type(self, widget):
		store = self.slags.get_model()
		self.add_single_item(store)		
	
	def edit_type(self, widget):
		item = self.get_selected_combo(self.slags)
		NoteEditor(item, self.do_type_edit)

	def do_type_edit(self, new_item, old_item):
		store = self.slags.get_model()
		self.modify_single_item(new_item, old_item, store)
				
	def remove_type(self, widget):
		self.delete_row(self.slags)
  	
  		# Notes
  	def new_note(self, widget):
		store = self.notes.get_model()
		self.add_single_item(store)

	def edit_note(self, widget):
		item = self.get_selected_combo(self.notes)
		NoteEditor(item, self.do_note_edit)
	
	def do_note_edit(self, new_item, old_item):
		store = self.notes.get_model()
		self.modify_single_item(new_item, old_item, store)
		
	def remove_note(self, widget):
		self.delete_row(self.notes)

	def modify_single_item(self, new_item, old_item, store):
		old_title = old_item.get_title()
			
		for item in store:
			text = item[0]
			if text == old_title:
				item[0] = new_item.get_title()
				break

	def add_single_item(self, store):
		editor = NoteEditor(None)
		result = editor.run()
		if result == 1:
			item = editor.new_note
			store.append([item.get_title(), item])
		
		editor.destroy()

  	def _init_signal_connections(self):
		SIGNAL_CONNECTIONS_DIC = {
	#		"on_cancel": self.cancel,
	#		"on_response": self.response,
			
			#Type
			"on_new_slags": self.new_type,
			"on_edit_slags": self.edit_type,
			"on_remove_slags": self.remove_type,
			
			#Note
            "on_new_note": self.new_note,
			"on_edit_note": self.edit_note,
			"on_remove_note": self.remove_note,            
						
			"on_delete_cancel": lambda x: x.hide
        	}
		self.builder.connect_signals(SIGNAL_CONNECTIONS_DIC)
#		self.gui.signal_autoconnect(SIGNAL_CONNECTIONS_DIC)
		
  	#def cancel(self, widget):
#		self.editor.destroy()
		
#	def response(self, widget):	
#		name = self.name.get_text()
#		price = self.price.get_value()	
#
#		slags = self.get_selected_combo(self.slags)
#		note = self.get_selected_combo(self.notes)
		
#		if self.old_row != []:
#			print self.old_row			
#			old_slags = self.old_row[2]
#			if old_slags.get_sid() != slags.get_sid():
#				old_slags.remove_wish()
#				slags.add_wish()
		
#			old_note = self.old_row[3]
#			if old_note.get_nid() != note.get_nid():
#				old_note.remove_wish()
#				note.add_wish()
#			print old_slags
#			print old_note	 
#		else:
#			slags.add_wish()
#			note.add_wish()		
		
#		self.response(gtk.RESPONSE_OK)

		
		#self.response([name, price, slags.title, note.title, slags, note])					
		#self.editor.destroy()		
