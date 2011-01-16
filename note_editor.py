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
import copy

from __init__ import GnomeConfig
from note import Note

class NoteEditor:
    
    last_nid = 0
    
    def __init__(self, item, callback):
        self.callback = callback
        self.item = item
        self._init_gui()
    
    def _init_gui(self):
        self.gui = gtk.glade.XML(GnomeConfig.main_gui, "edit_new")
        self._init_alias()
        if self.item != None:
            self.title.set_text(self.item.get_title())
            self.text.set_text(self.item.get_text())
            
        self._init_signal_connections()
            
    def _init_alias(self):
        self.editor = self.gui.get_widget("edit_new")
        self.title = self.gui.get_widget("edit_title")
        self.text = self.gui.get_widget("edit_text")
    
    
    def _init_signal_connections(self):
        SIGNAL_CONNECTIONS_DIC = {
            "on_cancel": self.cancel,
            "on_accept": self.accept,
        #    "on_response": self.response,
            "on_delete_cancel": lambda x: x.hide
            }
        self.gui.signal_autoconnect(SIGNAL_CONNECTIONS_DIC)
        
    def accept(self, widget):
        title = self.title.get_text()
        text = self.text.get_text()
        if self.item == None:
            new_note = Note(title, text)
            self.callback(new_note)
        else:
            old_item = copy.deepcopy(self.item)
            self.item.set_title(title)
            self.item.set_text(text)
            self.callback(self.item, old_item)
        self.editor.destroy()
            
    def cancel(self, widget):
        self.editor.destroy()