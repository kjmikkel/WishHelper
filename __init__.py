# -*- coding: utf-8 -*-
#This is the gnome_frontend package. It's a GTK interface that want to be
#simple, HIG compliant and well integrated with Gnome.
import os
from note import Note
from enumerate import Enumerate

class GnomeConfig:

	current_rep = os.path.dirname(os.path.abspath(__file__))
	current_rep = os.path.join(current_rep, "gui")
	main_gui  	= os.path.join(current_rep, "WishHelperMain.glade")
	helper_gui  = os.path.join(current_rep, "WishHelperEditor.glade")
	edit_gui 	= os.path.join(current_rep, "WishHelperEdit.glade")
	
	COL_TITLE     = 0
	COL_PRICE     = 1
	COL_TYPE      = 2
	COL_NOTE      = 3
	COL_TYPE_VAL  = 4
	COL_NOTE_VAL  = 5
		
	start_media_txt = ["Bog", "Computerspil", "DVD", "Køkenudstyr", "Værktøj"]
	start_media = []	

	start_notes = [Note("Ingen", "", 0)]	

	nid = 0	
	for med in start_media_txt:
		slags = Note(med, "", nid)
		start_media.append(slags)
    	nid += 1

