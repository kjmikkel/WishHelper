from __init__ import GnomeConfig

class Wish:
	""" A wish for birthdays, christmas or other events """

	def __init__(self, row):
		self.row = row
		self.title = row[GnomeConfig.COL_TITLE]
		self.price = row[GnomeConfig.COL_PRICE]
		self.type = row[GnomeConfig.COL_TYPE]
		self.note = row[GnomeConfig.COL_NOTE]

	def get_title(self):
		return self.title

	def set_title(self, new_title):
		self.row[GnomeConfig.COL_TITLE] = new_title		
		self.title = new_title

	def get_price(self):
		return self.price

	def set_price(self, new_price):
		self.row[GnomeConfig.COL_PRICE] = new_price		
		self.price = price

	def get_type(self):
		return self.type

	def set_type(self, new_type):
		self.row[GnomeConfig.COL_TYPE] = new_type
		self.type = new_type

	def get_note(self):
		return self.note

	def set_note(self, new_note):
		self.row[GnomeConfig.COL_NOTE] = new_note
		self.note = new_note

	def get_row(self):
		return self.row

	def __str__(self):
		s = "Task Object\n"
		s = s + "Title:  " + self.title + "\n"
		s = s + "Price:     " + str(self.price) + "\n"
		s = s + + str(self.type) + "\n"
		s = s + + str(self.note)
		return s
