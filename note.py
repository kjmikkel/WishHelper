class Note:
	
	def __init__(self, text, nid = None):
		self.text = text
		self.nid = nid
		self.wish_count = 0

	def get_nid(self):
		return self.nid

	def set_nid(self, nid):
		if not self.nid:
			self.nid = nid

	def can_delete():
		return self.wish_count == 0

	def has_wish():
		self.wish_count += 1

	def remove_wish():
		self.wish_count -= 1

	def __str__(self):
		if nid:
			return "Note: " + self.text + " (" + self.nid + ")"
		else:
			return "Note: " + self.text
