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
from slags import Slags
from note import Note
	
class WishEditor :
	def __init__(self, row, response, Slags = None, Notes = None):
		self._init_gui(Slags, Notes)						
		self._init_signal_connections()
		self.response = response		
		self.row = row		
		if self.row != []:
			print "row is not none"
		if Notes != None:
			note_store = self.note.get_model()
			print note_store
		if Slags != None:
			slags_store = self.slags.get_model()
			print slags_store	
	
	def fill_in_combobox(self, combobox, List, default_value):
		store = gtk.ListStore(str)

		# If we do not have anything List, then we fill it out with the default values
		if not List:
			List = default_value
		
		#for medie in List:			
		for i in List:
			store.append([str(i)])

		combobox.set_model(store)
		if len(List) > 0:		
			combobox.set_active(0)
		

	def _init_gui(self, Slags, Notes):
		self.gui = gtk.glade.XML(GnomeConfig.main_gui, "wish_editor")
		self._init_alias()
		
		self.fill_in_combobox(self.slags, Slags, GnomeConfig.start_media)
		self.fill_in_combobox(self.notes, Notes, [])
	

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

	def response(self, widget):
		
		name = self.name.get_text()
		price = self.price.get_value()
		slags = self.get_active_text(self.slags)  				
		note = self.get_active_text(self.notes)
		
		# temp value:
		if slags == None or note == None:
			slags = ""
			note = ""
		if slags != None or note == None:		
			self.response([name, price, slags, note])					
		self.editor.destroy()		
		
  	def cancel(self, widget):
		self.editor.destroy()

  	def new_note(self, widget):
		print "new note"

  	def new_type(self, widget):
		print "new type"

  	def _init_signal_connections(self):
		SIGNAL_CONNECTIONS_DIC = {
			"on_cancel": self.cancel,
			"on_response": self.response,
            "on_new_note": self.new_note,
            "on_new_type": self.new_type,
			"on_delete_cancel": lambda x: x.hide
        	}
		self.gui.signal_autoconnect(SIGNAL_CONNECTIONS_DIC)
