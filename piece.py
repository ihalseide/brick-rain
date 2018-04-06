#!/usr/bin/env python3

import random

COLORS = ['red', 'blue', 'white', 'black', 'green', 'orange']

# o = block, / = next row, _ = blank
SHAPES = {
	'O': 'oo/oo',
	'J': 'o/ooo',
	'L': 'ooo/o',
	'I': 'oooo',
	'S': '_oo/oo',
	'Z': 'oo/_oo',
	'T': 'ooo/_o',
	'.': 'o'
}


class Piece:

	@staticmethod
	def to_array(shape_string, yes='o', no='_', next_row='/'):
		rows = shape_string.split(next_row)
		height = len(rows)
		width = max(len(r) for r in rows)
		arr = [[None for x in range(width)] for y in range(height)]
		#print('Rows: %s'%rows)
		#print('Size: %sx%s'%(width, height))
		for x in range(width):
			for y in range(height):
				try:
					value = rows[y][x]
				except IndexError:
					value = None
				if value is not None:
					if value == no:
						continue
					else:
						arr[y][x] = yes
		return arr


	# x, y on board, shape is either string or shape key
	def __init__(self, parent, x, y, shape, color, box_size):
		self.parent = parent

		self.x = x
		self.y = y

		self.color = color
		self.shape = shape

		self.box_size = box_size


	def rotate(self):
		center = (self.width//2, self.height//2)
		self.shape = list(list(x) for x in zip(*reversed(self.shape))) # zip & reversed rotates the array
		new_center = (self.width//2, self.height//2)
		self.x -= new_center[0] - center[0]
		self.y -= new_center[1] - center[1]
		return self


	@property
	def max_size(self):
		return max([self.width, self.height])

	@property
	def width(self):
		return len(self.shape[0])


	@property
	def height(self):
		return len(self.shape)


	def get_at(self, x, y):
		return self.shape[y][x]


	def draw(self, screen, pixel_x=None, pixel_y=None):
		if pixel_x is None and pixel_y is None:
			pixel_x, pixel_y = self.parent.to_pixel_coords(self.x, self.y)
		for x in range(self.width):
			for y in range(self.height):
				value = self.get_at(x, y)
				if value:
					self.parent.draw_box(screen, None, None, self.color, pixel_x + (self.box_size*x), pixel_y + (self.box_size*y))


	# debug:
	def __str__(self):
		return str(self.shape)


	def __repr__(self):
		return 'Piece(x=%s, y=%s, shape=%s, rotation=%s, color=%s)'%(self.x, self.y, self.shape, self.rotation, self.color)