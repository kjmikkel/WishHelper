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

class NoteEditor(object):
    
    last_nid = 0
    
    def __init__(self, item):
        self.item = item
        self._init_gui()
              
    def run(self):
        return self.editor.run()
    
    def destroy(self):
        self.editor.destroy()
    
    def _init_gui(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(GnomeConfig.edit_gui)
            
        self._init_alias()
        
        if self.item != None:
            self.title_text.set_text(self.item.get_title())
            self.text_text.set_text(self.item.get_text())
            
        self._init_signal_connections()
            
    def _init_alias(self):
        self.editor = self.builder.get_object("edit_new")
        self.title_text = self.builder.get_object("edit_title")
        self.text_text = self.builder.get_object("edit_text")    
    
    def _init_signal_connections(self):
        SIGNAL_CONNECTIONS_DIC = {
            "on_accept": self.accept,
            }
        self.builder.connect_signals(SIGNAL_CONNECTIONS_DIC)
        
    def accept(self, widget):
        title = self.title_text.get_text()
        text = self.text_text.get_text()
        self.new_note = Note(title, text)