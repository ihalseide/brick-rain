#!/usr/bin/env python3

import pygame

from base_scene import BaseScene
from game_resources import SOUNDS


BIG_FONT = pygame.font.Font('freesansbold.ttf', 25)
NORMAL_FONT = pygame.font.Font('freesansbold.ttf', 15)


class GameOverScene(BaseScene):

	def __init__(self, score, level, retry_scene):
		super().__init__()

		self.score = score
		self.level = level
		self.retry_scene = retry_scene # what scene to switch back to if 'retry' is selected

		self.retry_button = pygame.Rect(100, 250, 150, 30)
		self.quit_button = pygame.Rect(100, 300, 150, 30)

		pygame.mixer.music.pause()
		SOUNDS['over'].play()

		# only display once
		self.has_drawn = False


	def display(self, screen):
		# everything here only needs to be displayed once
		if self.has_drawn:
			return
		else:
			self.has_drawn = True

		screen.fill((0,0,0))

		# show game over and score...
		surf = BIG_FONT.render('GAME OVER', True, (255, 255, 255), (0,0,0))
		game_over_rect = surf.get_rect()
		game_over_rect.center = screen.get_rect().center
		game_over_rect.y = 100
		screen.blit(surf, game_over_rect)

		surf = NORMAL_FONT.render('Score: %s, Level: %s'%(self.score, self.level), True, (100, 100, 255), (0,0,0))
		surf_rect = surf.get_rect()
		surf_rect.midtop = game_over_rect.midbottom
		screen.blit(surf, surf_rect)

		# draw buttons with text
		pygame.draw.rect(screen, (0, 0, 255), self.retry_button, 5)
		pygame.draw.rect(screen, (0, 0, 0), self.retry_button)
		surf = 	NORMAL_FONT.render('Retry (R)', True, (255, 255, 255))
		surf_rect = surf.get_rect()
		surf_rect.center = self.retry_button.center
		screen.blit(surf, surf_rect)

		pygame.draw.rect(screen, (255, 0, 0), self.quit_button, 5)
		pygame.draw.rect(screen, (0, 0, 0), self.quit_button)
		surf = 	NORMAL_FONT.render('Quit (Esc)', True, (255, 255, 255))
		surf_rect = surf.get_rect()
		surf_rect.center = self.quit_button.center
		screen.blit(surf, surf_rect)


	def update(self):
		pass


	def process_inputs(self, events, pressed_keys):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.retry_button.collidepoint(pygame.mouse.get_pos()):
					self.switch_to_scene(self.retry_scene)
				elif self.quit_button.collidepoint(pygame.mouse.get_pos()):
					self.terminate()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_r:
					self.switch_to_scene(self.retry_scene)
