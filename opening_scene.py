#!/usr/bin/env python3

import os
import pygame
import random
import time
import json

from base_scene import BaseScene
from game_scene import GameScene
from piece import Piece, COLORS
from game_resources import IMAGES


class OpeningScene(BaseScene):

	box_size = 20

	def __init__(self):
		super().__init__()

		self.title = IMAGES['title']
		self.title_rect = self.title.get_rect()

		self.start_time = time.time()
		self.min_time = 2 # seconds until user can begin
		self.font = pygame.font.Font('freesansbold.ttf', 14)
		font = pygame.font.Font('freesansbold.ttf', 28)
		self.text = font.render('Press a key to start', False, (255,255,255))
		self.text_rect = self.text.get_rect()
		self.gotten_text_center = False # need to wait for display to init.

		self.last_piece_time = time.time()
		self.wait_time = 0
		self.wait_range = 0.5, 2
		self.piece_speed = 3
		self.pieces = []

		#self.get_scores()


	def get_scores(self):
		filename = 'scores.json'
		if not os.path.isfile(filename):
			with open(filename, 'w+') as file:
				file.write([])

		with open(filename) as file:
			data = json.load(file)
		if data:
			self.top_3_scores = data.sort(key=lambda d: d['score'])[:2]
		else:
			self.top_3_scores = None


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


	def draw_scores(self, screen):
		return
		text = self.font.render('SCORES', False, (255,255,255))
		rect = text.get_rect()
		rect.center = (180, 70)
		screen.blit(text, rect)

		if self.top_3_scores:
			for i, score in enumerate(self.top_3_scores):
				if i == 0 and time.time() - self.last_Flash_time >= self.flash_wait:
					color = (255, 255, 255)
					self.last_flash_time = time.time()
				else:
					color = (0, 0, 255)

				value = '%s %s' %(score['name'], score['score'])
				text = self.font.render(value, False, color)
				rect = text.get_rect()
				rect.center = 100 + 30*i
				screen.blit(text, rect)
		else:
			text = self.font.render('No High Scores', False, (255,255,255))
			rect = text.get_rect()
			rect.center = (180, 100)
			screen.blit(text, rect)


	def display(self, screen):
		screen.fill((0,0,0))
		self.draw_pieces(screen)
		self.draw_start(screen)
		#self.draw_scores(screen)
		screen.blit(self.title, self.title_rect)


	def draw_start(self, screen):
		if not self.gotten_text_center:
			try:
				r = pygame.display.get_surface().get_rect()
				self.text_rect.centerx = r.centerx
				self.text_rect.centery = 2/3*r.height
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