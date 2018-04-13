#!/usr/bin/env python3

import pygame
import random
import time

from base_scene import BaseScene
from game_scene import GameScene
from piece import Piece, SHAPES, COLORS
from game_resources import IMAGES


class OpeningScene(BaseScene):

	box_size = 20

	def __init__(self):
		super().__init__()
		
		self.title = IMAGES['title']
		self.title_rect = self.title.get_rect()
		
		self.start_time = time.time()
		self.min_time = 2 # seconds until user can begin
		font = pygame.font.Font('freesansbold.ttf', 28)
		self.text = font.render('Press a key to start', False, (255,255,255))
		self.text_rect = self.text.get_rect()
		self.gotten_text_center = False # need to wait for display to init.
		
		self.last_piece_time = time.time()
		self.wait_time = 0
		self.wait_range = 0.5, 2
		self.piece_speed = 3
		self.pieces = []
		
		
	@property
	def can_begin(self):
		return time.time() - self.start_time >= self.min_time

		
	def new_piece(self):
		# x with some padding
		x = random.randint(self.box_size, pygame.display.get_surface().get_rect().width - self.box_size)
		y = -self.box_size
		color = random.choice(COLORS)
		piece = Piece(self, x, y, '*', color, self.box_size)
		return piece
		
		
	def process_inputs(self, events, pressed_keys):
		if any(pressed_keys) and self.can_begin:
			self.switch_to_scene(GameScene())
		
		
	def display(self, screen):
		screen.fill((0,0,0))
		self.draw_pieces(screen)
		self.draw_start(screen)
		screen.blit(self.title, self.title_rect)
		
		
	def draw_start(self, screen):
		if not self.gotten_text_center:
			try:
				self.text_rect.center = pygame.display.get_surface().get_rect().center
				self.gotten_text_center = True
			except AttributeError:
				self.gotten_text_center = False
		if self.can_begin and self.gotten_text_center:
			screen.blit(self.text, self.text_rect)
			
			
	def draw_pieces(self, screen):
		for piece in self.pieces:
			piece.draw(screen, piece.x, piece.y)
			
			
	# required by the pieces
	def draw_box(self, screen, box_x, box_y, color, pixel_x, pixel_y, draw_blank=False):
		the_rect = (pixel_x, pixel_y, self.box_size, self.box_size)
		screen.blit(IMAGES[color+' brick'], the_rect)
		
		
	def generate_pieces(self):
		if time.time() - self.last_piece_time >= self.wait_time:
			self.pieces.append(self.new_piece())
			self.last_piece_time = time.time()
			self.wait_time = random.uniform(*self.wait_range)
			
			
	def update(self):
		self.generate_pieces()
		# update pieces
		for piece in self.pieces:
			piece.y += self.piece_speed
			if piece.y > pygame.display.get_surface().get_rect().height:
				self.pieces.remove(piece)