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
#   along with WishHelper.  If not, see <http://www.gnu.org/licenses/>.

from __init__ import GnomeConfig

class Wish:
  """ A wish for birthdays, christmas or other events """

  def __init__(self, data):
    
    if not isinstance(data, tuple):
      row = data
      self.row = row
      self.num = row[GnomeConfig.COL_NUMBER]
      self.title = row[GnomeConfig.COL_TITLE]
      self.price = row[GnomeConfig.COL_PRICE]
      self.type = row[GnomeConfig.COL_TYPE]
      self.note = row[GnomeConfig.COL_NOTE]
    else:
      data = data[0]
      self.row = range(0, 5)
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

  #Note
  def get_note(self):
    return self.note

  def set_note(self, new_note):
    self.row[GnomeConfig.COL_NOTE] = new_note
    self.note = new_note
    
  def get_row(self):
    return self.row

  def list_rep(self):
    return [self.num, self.title, self.price, self.type, self.note]

  def __str__(self):
    s = "Task Object\n"
    s += "Title:\t" + self.title + "\n"
    s += "Price:\t" + str(self.price) + "\n"
    s += str(self.type) + "\n"
    s += str(self.note)
    return s
