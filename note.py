# -*- coding: utf-8 -*-
class Note:
	
	def __init__(self, title, text, nid = None):		
		self.title = title
		self.text = text
		self.nid = nid
		self.wish_count = 0

	def get_nid(self):
		return self.nid

	def set_nid(self, nid):
		if not self.nid:
			self.nid = nid

	def can_delete(self):
		return self.wish_count == 0

	def add_wish(self):
		self.wish_count += 1

	def remove_wish(self):
		self.wish_count -= 1

	def get_title(self):
		return self.title

	def get_text(self):
		return self.text

	def set_text(self, text):
		self.text = text
		
	def __str__(self):
		text = "Note: " + self.title +  ": " + self.text
		if self.nid:
			text += " (" + self.nid + ")"
		return text
