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

from wisheditor import WishEditor
from __init__ import GnomeConfig
from wish import Wish
from note import Note
from slags import Slags



class WishTreeView(gtk.TreeView):
	"""TreeView for display of a list of task. Handles DnD primitives too."""

	def __init__(self, model=None):
		gtk.TreeView.__init__(self)
		self.columns = []
		self.show()

	def get_column(self, index):
		return self.columns[index]

	def get_column_index(self, col_id):
		return self.columns.index(col_id)

	def refresh(self, collapsed_rows=None):
		self.expand_all()
		self.get_model().foreach(self._refresh_func, collapsed_rows)

	def _refresh_func(self, model, path, iter, collapsed_rows=None):
		if collapsed_rows:
			tid = model.get_value(iter, COL_TID)
			if tid in collapsed_rows:
				self.collapse_row(path)
		model.row_changed(path, iter)

class ActiveWishTreeView(WishTreeView):
	"""TreeView for display of a list of wishes. Handles DnD primitives too."""

	DND_TARGETS = [
		('gtg/task-iter-str', gtk.TARGET_SAME_WIDGET, 0)
	]

	def __init__(self):
		WishTreeView.__init__(self)
		self._init_tree_view()

		# Drag and drop
		self.enable_model_drag_source(\
			gtk.gdk.BUTTON1_MASK,
			self.DND_TARGETS,
			gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
		self.enable_model_drag_dest(\
			self.DND_TARGETS,
			gtk.gdk.ACTION_DEFAULT)
 	
		self.drag_source_set(\
			gtk.gdk.BUTTON1_MASK,
			self.DND_TARGETS,
			gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
	
		self.drag_dest_set(\
			gtk.DEST_DEFAULT_ALL,
			self.DND_TARGETS,
			gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
	
		self.connect('drag_drop', self.on_drag_drop)
		self.connect('drag_data_get', self.on_drag_data_get)
		self.connect('drag_data_received', self.on_drag_data_received)

	def create_column(self, label, place):
		title_col   = gtk.TreeViewColumn()
		render_text = gtk.CellRendererText()
		render_text.set_property("ellipsize", pango.ELLIPSIZE_END)
		title_col.set_title(label)
		title_col.pack_start(render_text, expand=True)
		title_col.add_attribute(render_text, "markup", place)
		title_col.set_resizable(True)
		title_col.set_expand(True)		
		title_col.set_sort_column_id(place)
		self.append_column(title_col)
		self.columns.insert(place, title_col)
		return title_col

	def _init_tree_view(self):
		# Columns
		name_col  = self.create_column("Navn", GnomeConfig.COL_TITLE)
		price_col = self.create_column("Pris", GnomeConfig.COL_PRICE)
		type_col  = self.create_column("Type", GnomeConfig.COL_TYPE)
		note_col  = self.create_column("Note", GnomeConfig.COL_NOTE)	

		# Global treeview properties
		self.set_property("expander-column", name_col)
		self.set_property("enable-tree-lines", False)
		self.set_rules_hint(False)

	### DRAG AND DROP ########################################################

	def on_drag_drop(self, treeview, context, selection, info, timestamp):
		self.emit_stop_by_name('drag_drop')

	def on_drag_data_get(self, treeview, context, selection, info, timestamp):
		"""Extract data from the source of the DnD operation. Here the id of
		the parent task and the id of the selected task is passed to the
		treeselection = treeview.get_selection()
		destination"""
		treeselection = treeview.get_selection()
		model, iter = treeselection.get_selected()
		iter_str = model.get_string_from_iter(iter)
		selection.set('gtg/task-iter-str', 0, iter_str)
		return

	def delete_row(self):
		model = self.get_model()
		selection = self.get_selection().get_selected()
		selected_row = selection[1]		
		if selected_row != None:	
	  		model.remove(selected_row)

	def insert_row(self):
		row = []
		WishEditor(row, self.insert_row_response)
		
	def insert_row_response(self, row):
		print "new_response:", row		
		if row != [] and row != None:
			liststore = self.get_model()
			liststore.append(row)

	def edit_row(self):
		model = self.get_model()
		self.active = self.get_selection().get_selected()[1]
		if self.active != None:
			row = model.get(self.active, 0, 1, 4, 5)
			WishEditor(row, self.edit_row_response)

	def edit_row_response(self, row):
		listStore = self.get_model()
		listStore.insert_after(self.active, row)
		listStore.remove(self.active)
			
			
	def on_drag_data_received(self, treeview, context, x, y, selection, info,\
							  timestamp):
		model = treeview.get_model()
		drop_info = treeview.get_dest_row_at_pos(x, y)
		drag_iter = model.get_iter_from_string(selection.data)	
		if drop_info:	
			path, position = drop_info		
			iter = model.get_iter(path)	
	  
			if position == gtk.TREE_VIEW_DROP_BEFORE:
				model.move_before(drag_iter, iter)
	  		elif position == gtk.TREE_VIEW_DROP_AFTER:
				model.move_after(drag_iter, iter)	 
		else:
	  		model.move_before(drag_iter, None)
		
		self.emit_stop_by_name('drag_data_received')

	
class GUI:
	def __init__(self):
		# Load window tree		
		self._init_aliases()		
		self._init_gui()
		self._init_signal_connections()	
		self.current_row = None
	
		# Show the gui		
		self.window.show()
		gtk.main()

	def add_wish(self, widget):	
		self.task_tv.insert_row()
	
	def on_edit_wish(self, widget):		
		self.task_tv.edit_row()

	def on_delete_wish(self, widget):
		self.task_tv.delete_row()
 
	def on_close(self, widget):
		print "close"
 
	def _init_gui(self):
		self.model = gtk.ListStore(
		str,		
		int,
		str,
		str,
		gobject.TYPE_PYOBJECT, 
		gobject.TYPE_PYOBJECT)

		self.task_tv = ActiveWishTreeView()
		self.task_tv.set_model(self.model)		
		self.wishlist.add(self.task_tv)
		
	def _init_aliases(self):	
		self.gui = gtk.glade.XML(GnomeConfig.main_gui, "MainWindow")
		self.window = self.gui.get_widget("MainWindow")
		self.wishlist = self.gui.get_widget("WishList")
	
	def _init_signal_connections(self):
		SIGNAL_CONNECTIONS_DIC = {
			"on_add_wish": self.add_wish,
			"on_cancel": self.cancel,
			"on_edit_wish": self.on_edit_wish,
			"on_delete_wish": self.on_delete_wish,
			"gtk_main_quit": self.on_close
		}
		self.gui.signal_autoconnect(SIGNAL_CONNECTIONS_DIC)

	def get_selected_task(self, tv=None):
		"""Return the 'uid' of the selected task

		:param tv: The tree view to find the selected task in. Defaults to
			the task_tview.
		"""
		tview = self.task_tv
		# Get the selection in the gtk.TreeView
		selection = tview.get_selection()
		#If we don't have anything and no tview specified
		#Let's have a look in the closed task view
		if selection and selection.count_selected_rows() <= 0 and not tv:
			tview = self.ctask_tv
			selection = tview.get_selection()
		if selection:
			model, selection_iter = selection.get_selected()
			if selection_iter:
				ts  = tview.get_model()
		return selection
	
	def cancel(self, widget):
		self.window.destroy()

try:
	sys.exit(GUI())
except KeyboardInterrupt:
	sys.exit(1)

