#!/usr/bin/env python3


import pygame
import random

from game_resources import IMAGES


class Cloud(pygame.sprite.Sprite):


	def __init__(self, location, min_x, max_x):
		pygame.sprite.Sprite.__init__(self)
		
		self.min_x = min_x
		self.max_x = max_x
		
		self.image = IMAGES['cloud']
		self.rect = self.image.get_rect()
		
		self.double_speed = bool(random.randint(0,1))
		
		self.begin_floating = False
		self.floating = False
		
		if not self.double_speed:
			self.image = pygame.transform.scale(self.image, (self.rect.width//2, self.rect.height//2))
			self.rect = self.image.get_rect()
			self.should_move = True
		
		self.rect.center = location
		
		
	def float_on_click(self):
		if pygame.mouse.get_pressed()[0]:
			if self.rect.collidepoint(pygame.mouse.get_pos()):
				self.begin_floating = True
		# only run this block once
		if self.begin_floating:
			# need values for easing
			self.start_y = self.rect.centery
			self.stop_y = self.start_y - random.randint(10, 40)
			self.step = 0.05
			self.percent = 0
			self.floating = True
		if self.floating:
			self.begin_floating = False
			if self.percent <= 1:
				self.rect.centery = self.start_y + ((self.stop_y-self.start_y) * self.percent)
				self.percent += self.step
				
				
	def update(self):
		self.float_on_click()
		if self.double_speed:
			self.rect.x += 1
		else:
			if self.should_move:
				self.rect.x += 1
			self.should_move = not self.should_move # move every other tick
				
		if self.rect.left > self.max_x:
			self.rect.right = self.min_x