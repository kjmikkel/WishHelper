# -*- coding: utf-8 -*-
#This is the gnome_frontend package. It's a GTK interface that want to be
#simple, HIG compliant and well integrated with Gnome.
import os
from note import Note

class GnomeConfig:

	current_rep = os.path.dirname(os.path.abspath(__file__))
	main_gui  	= os.path.join(current_rep, "WishHelperGUI.glade")
	#editor_gui	= os.path.join(current_rep, "wishEditor.glade")
	
	COL_TITLE     = 0
	COL_PRICE     = 1
	COL_TYPE      = 2
	COL_NOTE      = 3

	start_media_txt = ["Bog", "Computerspil", "DVD", "Køkenudstyr", "Værktøj"]
	start_media = []	

	start_notes = [Note("Ingen", "", 0)]	

	nid = 0	
	for med in start_media_txt:
		slags = Note(med, "", nid)
		start_media.append(slags)
    	nid += 1

