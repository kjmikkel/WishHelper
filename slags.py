# -*- coding: utf-8 -*-
class Slags():

	def __init__(self, title, sid = None):
		self.title = title
		self.sid = sid
		self.wish_count = 0

	def get_title(self):
		return self.title

	def get_sid(self):
		return self.sid

	def set_sid(self, sid):
		if not self.sid:
			self.sid = sid

	def can_delete():
		return self.wish_count == 0
	def has_wish():
		self.wish_count += 1

	def remove_wish():
		self.wish_count -= 1

	def __str__(self):
		if self.sid:
			return "Slags:", self.title + " (" + self.sid + ")"
		else:
			return "Slags:", self.title
