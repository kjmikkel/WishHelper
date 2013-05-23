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

from __init__ import GnomeConfig

class Wish:
  """ A wish for birthdays, christmas or other events """

  def __init__(self, data):
    
    if not isinstance(data, tuple):
    #  print "list"
      row = data
      self.row = row
      self.num = row[GnomeConfig.COL_NUMBER]
      self.title = row[GnomeConfig.COL_TITLE]
      self.price = row[GnomeConfig.COL_PRICE]
      self.type = row[GnomeConfig.COL_TYPE]
      self.note = row[GnomeConfig.COL_NOTE]
      self.type_val = row[GnomeConfig.COL_TYPE_VAL]
      self.note_val = row[GnomeConfig.COL_NOTE_VAL]
    else:
    #  print "not list"
      data = data[0]
      self.row = range(0, 7)
      self.set_title(data[0])
      self.set_price(data[1])
      self.set_type(data[2])
      self.set_note(data[3])
      self.set_number(data[4])
      
  def get_title(self):
    return self.title

  def set_title(self, new_title):
    self.row[GnomeConfig.COL_TITLE] = new_title    
    self.title = new_title

  def get_price(self):
    return self.price

  def set_price(self, new_price):
    self.row[GnomeConfig.COL_PRICE] = new_price    
    self.price = new_price

  def get_number(self):
    return self.num

  def set_number(self, new_number):
    self.row[GnomeConfig.COL_NUMBER] = new_number
    self.num = new_number

  #Type
  def get_type(self):
    return self.type
  
  def set_type(self, new_type):
    self.row[GnomeConfig.COL_TYPE] = new_type  
    self.type = new_type

  def set_type_val(self, new_type):
    self.row[GnomeConfig.COL_TYPE_val] = new_type  
    self.type = new_type

  #Note
  def get_note(self):
    return self.note

  def set_note(self, new_note):
    self.row[GnomeConfig.COL_NOTE] = new_note
    self.note = new_note

  def set_note_val(self, new_note):
    self.row[GnomeConfig.COL_NOTE_VAL] = new_note
    self.note = new_note
    
  def get_note_val(self):
    return self.note_val
    
  def set_type_val(self, type_val):
    self.row[GnomeConfig.COL_TYPE_VAL] = type_val
    self.type_val = type_val
    
  def get_type_val(self):
    return self.type_val

  def get_row(self):
    return self.row

  def __str__(self):
    s = "Task Object\n"
    s += "Title:\t" + self.title + "\n"
    s += "Price:\t" + str(self.price) + "\n"
    s += str(self.type) + "\n"
    s += str(self.note)
    return s
