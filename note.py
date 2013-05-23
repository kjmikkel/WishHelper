# -*- coding: utf-8 -*-

#    This file is part of WishHelper.
#
#   WishHelper is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   WishHelper is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with The Lonely Runner Verifier.  If not, see <http://www.gnu.org/licenses/>.

class Note():

  def __init__(self, title, text = "", nid = 0):
    self.title = title
    self.text = text    
    self.nid = nid
    self.wish_count = 0

  def get_title(self):
    return self.title
  
  def set_title(self, new_title):
    self.title = new_title

  def get_id(self):
    return self.nid

  def set_id(self, nid):
    if not self.nid:
      self.nid = nid

  def can_delete(self):
    return self.wish_count == 0
  
  def add_wish(self):
    self.wish_count += 1

  def remove_wish(self):
    self.wish_count -= 1
  
  def get_text(self):
    return self.text

  def set_text(self, new_text):
    self.text = new_text

  def semi_serilize(self):
    return str(self.get_title()), str(self.get_text()), str(self.get_id()) 

  def __str__(self):
    text = self.title + ": " + self.text
    if self.nid:
      text += " (" + self.nid + ")"
    return text
