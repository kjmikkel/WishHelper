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
import json
import datetime
import re
import textwrap
from configobj import ConfigObj
import exceptions

from wish_editor import WishEditor
from __init__ import GnomeConfig
from wish import Wish
from note import Note

class WishTreeView(gtk.TreeView):
  """TreeView for display of a list of task. Handles DnD primitives too."""

  def __init__(self, model=None):
    gtk.TreeView.__init__(self)
    self.columns = []
    self.set_reorderable(True)
    self.show()

  def get_column(self, index):
    return self.columns[index]

  def get_column_index(self, col_id):
    return self.columns.index(col_id)

  def refresh(self, collapsed_rows=None):
    self.expand_all()
    self.get_model().foreach(self._refresh_func, collapsed_rows)

  def _refresh_func(self, model, path, cur_iter, collapsed_rows=None):
    if collapsed_rows:
      tid = model.get_value(cur_iter, COL_TID)
      if tid in collapsed_rows:
        self.collapse_row(path)
    model.row_changed(path, cur_iter)

class ActiveWishTreeView(WishTreeView):
  """TreeView for display of a list of wishes. Handles DnD primitives too."""

  DND_TARGETS = [
    ('gtg/task-iter-str', gtk.TARGET_SAME_WIDGET, 0)
    ]

  def __init__(self):
    self.Notes = GnomeConfig.start_notes
    self.Slags = GnomeConfig.start_media
    
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
    title_col = gtk.TreeViewColumn()
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
    num_col = self.create_column("#", GnomeConfig.COL_NUMBER)
    size = 35
    num_col.set_resizable(False)
    num_col.set_clickable(True)
    num_col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
    num_col.set_expand(False)
    num_col.set_fixed_width(size)
    num_col.set_max_width(size)
    
    name_col = self.create_column("Navn", GnomeConfig.COL_TITLE)
    price_col = self.create_column("Pris", GnomeConfig.COL_PRICE)
    type_col = self.create_column("Type", GnomeConfig.COL_TYPE)
    note_col = self.create_column("Note", GnomeConfig.COL_NOTE)  

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
    model, cur_iter = treeselection.get_selected()
    iter_str = model.get_string_from_iter(cur_iter)
    selection.set('gtg/task-iter-str', 0, iter_str)     
    return

  def delete_row(self):
    selection = self.get_selection()
    model, selected = selection.get_selected()
    if selected:
      row_num = len(model)
      path = model.get_path(selected)
      row = path[0]
      if row_num > 1 and row == 0:
        selection.select_path(1)
      else:
        selection.select_path(row - 1)
      model.remove(selected)
    
    row_number = 1
    for row in self.get_model():
      row[0] = row_number
      row_number += 1
      

  def insert_row(self):
    editor = WishEditor([], self.Slags, self.Notes)
    result = editor.run()
    
    if result == 1:
      name = editor.name.get_text()
      price = editor.price.get_value()
      
      slags = editor.get_selected_combo(editor.slags)
      note = editor.get_selected_combo(editor.notes)
      
      if len(name) > 0 and price >= 0:
        liststore = self.get_model()
        new_number = len(liststore) + 1
        liststore.append([new_number, name, price, slags.title, note.title, slags, note])
      
      self.Slags = editor.Slags
      self.Notes = editor.Notes
    
    editor.destroy()
    
  def edit_row(self):
    model = self.get_model()
    self.active = self.get_selection().get_selected()[1]
    if self.active != None:
      row = model.get(self.active, 1, 2, 5, 6)
      print row
      editor = WishEditor(row, self.Slags, self.Notes)
      result = editor.run()
    
      if result == 1:
        listStore = self.get_model()
        
        name = editor.name.get_text()
        price = editor.price.get_value()
      
        slags = editor.get_selected_combo(editor.slags)
        note = editor.get_selected_combo(editor.notes)
      
        number = model.get(self.active, 0)[0]
        
        if len(name) > 0 and price >= 0:
          listStore.insert_after(self.active, [number, name, price, slags.title, note.title, slags, note])
          listStore.remove(self.active)
          liststore = self.get_model()
      
      self.Slags = editor.Slags
      self.Notes = editor.Notes
      
      editor.destroy()
      
  def on_drag_data_received(self, treeview, context, x, y, selection, info, \
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
    
    # Update row numbers
    row_number = 1
    for row in self.get_model():
      row[0] = row_number
      row_number += 1

    self.emit_stop_by_name('drag_data_received')
  
class GUI:
  def __init__(self):
    # Load window tree        
    self._init_gui()
    self._init_signal_connections()  
    self.current_row = None
  
    self.title_length = 38
    self.ini_file = "config.ini"
    # We give the default values for the variables
    self.load_path = None
    self.print_path = None
    if os.path.exists(self.ini_file):
      config = ConfigObj(self.ini_file)
      try:
        self.load_path = config['load_path']
        if not os.path.exists(self.load_path):
          self.load_path = None
      except KeyError:
        # Since we have already set the load and print path to None, there is no need to do anything in case of an exeception
        pass
      try:
        self.print_path = config['print_path']
        if not os.path.exists(self.print_path):
          self.print_path = None
      except KeyError:
        pass
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
    int,
    str,     
    int,
    str,
    str,
    gobject.TYPE_PYOBJECT,
    gobject.TYPE_PYOBJECT)
    self._init_aliases()
    self.gui.set_title("Ønske hjælper")
    # Add the icon for the program
    self.gui.set_icon_from_file("images/wishlist.png")
    now = datetime.datetime.now()
    self.year_text.set_value(now.year)

    self.task_tv = ActiveWishTreeView()
    self.task_tv.set_model(self.model)    
    self.wishlist.add(self.task_tv)
    self.latex_radio.set_active(True)

  def _init_aliases(self):  
    self.builder = gtk.Builder()
    self.builder.add_from_file(GnomeConfig.main_gui)
    
    self.gui = self.builder.get_object("MainWindow")

    self.window = self.builder.get_object("MainWindow")
    self.wishlist = self.builder.get_object("WishList")
    
    self.event_text = self.builder.get_object("event_text")
    self.year_text  = self.builder.get_object("year_spinner")
    self.year_check = self.builder.get_object("year_check")
    
    self.latex_radio = self.builder.get_object("latex_radio")
    
  #  self.gui = gtk.glade.XML(GnomeConfig.main_gui, "MainWindow")
  #  self.window = self.gui.get_widget("MainWindow")
  #  self.wishlist = self.gui.get_widget("WishList")
  
  def _init_signal_connections(self):
    SIGNAL_CONNECTIONS_DIC = {
      "on_add_wish": self.add_wish,
      "on_edit_wish": self.on_edit_wish,
      "on_delete_wish": self.on_delete_wish,

      "on_save": self.save,
      "on_load": self.load,
      "on_print": self.print_to_output_file,
      "on_cancel": self.cancel,
      
      "gtk_main_quit": self.on_close
    }
    self.builder.connect_signals(SIGNAL_CONNECTIONS_DIC)

  def save(self, widget):
    model = self.task_tv.get_model()
    
    slags = []
    notes = []
    wish = []
    
    for slags_item in self.task_tv.Slags:
      slags.append(slags_item.semi_serilize())
    
    for note_item in self.task_tv.Notes:
      notes.append(note_item.semi_serilize())
    
    for wish_item in model:
      wish_temp = Wish(wish_item)
      temp = [wish_temp.get_title(), wish_temp.get_price(), wish_temp.get_type(), wish_temp.get_note()]
      wish.append(temp)
    
    data = [slags, notes, wish, self.event_text.get_text(), self.year_text.get_value(), self.year_check.get_active()]
    write_value = json.dumps(data)
    
    chooser = gtk.FileChooserDialog(
             title="Gem dine ønsker", action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_SAVE, gtk.RESPONSE_OK
             ))
    filter = gtk.FileFilter()
    filter.set_name("Ønske filer | *.json")
    filter.add_pattern("*.json")
    chooser.add_filter(filter)
    chooser.set_default_response(gtk.RESPONSE_OK)

    if self.load_path:
      chooser.set_current_folder(self.load_path)

    response = chooser.run()    

    if response == gtk.RESPONSE_OK:  
      filename = chooser.get_filename()
      if not re.match("[^.]+.json$", filename):
        filename += ".json"

      file = open(filename, "w")
      file.write(write_value)
      file.close()

      self.load_path = os.path.dirname(filename)

    chooser.destroy()
    
  def load(self, widget):
    chooser = gtk.FileChooserDialog(
             title="Hent dine gemte ønsker",
             action=gtk.FILE_CHOOSER_ACTION_OPEN,
             buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_OPEN, gtk.RESPONSE_OK
             ))
    
    filter = gtk.FileFilter()
    filter.set_name("Ønske filer")
    filter.add_pattern("*.json")
    chooser.add_filter(filter)
    chooser.set_default_response(gtk.RESPONSE_OK)
    
    if self.load_path:
      chooser.set_current_folder(self.load_path)
    
    response = chooser.run()
    
    if response == gtk.RESPONSE_OK:
      file_name = chooser.get_filename()
      
      self.load_path = os.path.dirname(file_name)

      file = open(file_name, "r")
      file_data = file.read()
      file.close()
      
      data = json.loads(file_data)
      
      slags = data[0]
      notes = data[1]
      wish_list = data[2]
      self.event_text.set_text(data[3])
      self.year_text.set_value(data[4])
      self.year_check.set_active(data[5])
      
      Slags = []
      Notes = []
      Wish_ac = []

      #Instantiates the types and notes 
      for slags_item in slags:
        Slags.append(Note(slags_item[0], slags_item[1], slags_item[2]))
      
      for notes_item in notes:
        Notes.append(Note(notes_item[0], notes_item[1], notes_item[2]))

      self.syncronize_list(self.task_tv.Slags, Slags)
      self.syncronize_list(self.task_tv.Notes, Notes)

      wish_num = 1
      for wish_item in wish_list:
        
        wish_item.append(wish_num)
        input = (wish_item, 0)
        wish_val = Wish(input)
        wish_num +=1

        type_title = wish_val.get_type()
        note_title = wish_val.get_note()
         
  #     print "Type:", type_title
        for slags_item in self.task_tv.Slags:     
  #       print "Title:", slags_item.get_title()
          if type_title == slags_item.get_title():
            wish_val.set_type_val(slags_item)
            break
          
  #     print "Note:", note_title
        for note_item in self.task_tv.Notes:
  #       print "Title:", note_item.get_title()
          if note_title == note_item.get_title():
            wish_val.set_note_val(note_item)
            break
        
        final_wish = wish_val.get_row()
        Wish_ac.append(final_wish)
        
      print Wish_ac
      self.Slags = Slags
      self.Notes = Notes
      
      store = self.task_tv.get_model()
      store.clear()      
      for wish in Wish_ac:
        store.append(wish)
      
    chooser.destroy()
    
  def syncronize_list(self, list, load_list):
    for new_note in load_list:
      if new_note in list:
        continue
      else:
        title = new_note.get_title()
        found = False
        for old_note in list:
          if old_note.get_title() == title:
            old_note.set_text(new_note.get_text())
            found = True
            break
        
        if not found:
          list.append(new_note)

  def print_to_output_file(self, widget):
    latex_print = self.latex_radio.get_active()
    
    chooser_title = "Lav LaTeX fil"
    filter_pattern = "*.tex"
    filter_text = "LaTeX | " + filter_pattern
    
    if not latex_print:
      chooser_title = "Lav tekst fil"
      filter_pattern = "*.txt"
      filter_text = "Tekst | " + filter_pattern

    chooser = gtk.FileChooserDialog(
       title= chooser_title, action=gtk.FILE_CHOOSER_ACTION_SAVE,
          buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
       gtk.STOCK_SAVE, gtk.RESPONSE_OK
       ))

    filter = gtk.FileFilter()
    filter.set_name(filter_text)
    filter.add_pattern(filter_pattern)
      
    chooser.add_filter(filter)
    chooser.set_default_response(gtk.RESPONSE_OK)
    
    if self.print_path:
      chooser.set_current_folder(self.print_path)
    
    response = chooser.run()
      
    if response == gtk.RESPONSE_OK:
      
      if latex_print:
        data = self.print_latex()
        file_subfix = ".tex"
      else: 
        data = self.print_text()
        file_subfix = ".txt"

      if data != "":  
        filename = chooser.get_filename()

        if not re.match("[^.]+" + file_subfix + "$", filename):
          filename += file_subfix
      
        file = open(filename, "w")        
        data = data.encode('utf-8')
        file.write(data)
        file.close()
        # If we reach this point, then we are sure we have a valid filename, and we get and store the path
        self.print_path = os.path.dirname(filename)
        
    chooser.destroy()

  def print_text(self):
    new_line = os.linesep
    text = ""
    
    # We have to set the title
    title = self.event_text.get_text()
    if self.year_check.get_active():
      title = "Ønskeseddel til " + title + " for " + str(int(self.year_text.get_value()))
    
    text += title + new_line + new_line
    text += "Følgende ønsker er arrangeret fra mest ønskede til mindst" + new_line + new_line
  
    store = self.task_tv.get_model()
    amount_wishes = len(store)
      
    if amount_wishes == 0:
      return
    
    cur_iter = store.get_iter_first()
    current_wish = 0
  
    while cur_iter != None:
      if current_wish != 0:
        cur_iter = store.iter_next(cur_iter)
        if cur_iter == None:
          continue
      
      wish = store.get(cur_iter, 0, 1, 2)
      title = wish[GnomeConfig.COL_TITLE]
   
      price = str(wish[GnomeConfig.COL_PRICE])
        
      if price != "0":
         price += " kr."
      else:
        price = "?"
         
      slags = wish[GnomeConfig.COL_TYPE]
                      
      current_wish += 1  
      text += str(current_wish) + ".\t" + title + "\t\t\t" + slags + "\t" + price + new_line
        
    return text

  def print_latex(self):
      new_line = os.linesep
      path_sep = os.sep
      
      tn = "\\\\" + new_line
      sep = "\\hline"
      
      preamble_file = open("tex_files" + path_sep + "tex_header", "r")
      preamble = preamble_file.read()
      preamble_file.close()
    
      latex_str = preamble

      # We have to set the title
      title = self.event_text.get_text()
      if self.year_check.get_active():
        title = "Ønskeseddel til " + title + " for " + str(int(self.year_text.get_value())) 
      
      latex_str += "\\title{" + title + "}" + new_line
      latex_str += "\\begin{document}" + new_line
      latex_str += "\\maketitle" + new_line
      latex_str += "\\center" + new_line
      latex_str += "\\begin{minipage}{15.0cm}" + new_line
      latex_str += "\\begin{tabular}{llll}" + new_line
      latex_str += sep + new_line
      latex_str += "Priroritet & Navn & Type & Pris" + tn
      latex_str += sep + tn
        
      store = self.task_tv.get_model()
      amount_wishes = len(store)
      
      if amount_wishes == 0:
        return
      
      cur_iter= store.get_iter_first()
      current_wish = 0
      
      url = "(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F])+)*)"

      while cur_iter != None:
        if current_wish != 0:
          cur_iter = store.iter_next(cur_iter)  
          if cur_iter == None:
            continue
              
        wish = store.get(cur_iter, 0, 1, 2, 3, 4, 5, 6)
           
        title = wish[GnomeConfig.COL_TITLE]
        title_list = textwrap.wrap(title, self.title_length)           

        price = str(wish[GnomeConfig.COL_PRICE])
        if price != "0":
          price += " kr."
        else:
          price = "?"
           
        type = wish[GnomeConfig.COL_TYPE]

        note = wish[GnomeConfig.COL_NOTE_VAL]
           
        footnote = ""
        note_text = note.get_text()
        note_text = re.sub(url, "\url{\\1}", note_text)
        note_text = re.sub("%", "\\%", note_text)
           
        if note.get_title() != "Ingen":
          footnote = "\\footnote{" + note_text + "}"
           
        current_wish += 1  
        latex_str += str(current_wish) + ". & " + title_list[0] + footnote + " & " + type + " & " + price

        index = 1
        title_list_length = len(title_list)
        if title_list_length > 1:
          
          while index < title_list_length:
            latex_str += tn
            latex_str += " & " + title_list[index] + " & & " 
            index += 1
           
        if current_wish < amount_wishes:
          latex_str += tn
        else:
          latex_str += new_line
           
      latex_str += "\\end{tabular}\\par" + new_line
      latex_str += "\\vspace{1\\skip\\footins}" + new_line
      latex_str += "\\renewcommand{\\footnoterule}{}" + new_line
      latex_str += "\\end{minipage}" + new_line
      latex_str += "\end{document}"
      return latex_str
        
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
        ts = tview.get_model()
    return selection
  
  def cancel(self, widget):    
    config = ConfigObj(self.ini_file)
    if self.load_path:
      config['load_path'] = self.load_path
      config.write()
    if self.print_path:
      config['print_path'] = self.print_path
      config.write()
    
    self.window.destroy()
    sys.exit(0)

try:
  sys.exit(GUI())
except KeyboardInterrupt:
  sys.exit(1)

