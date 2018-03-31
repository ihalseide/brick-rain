#!/usr/bin/env python3

import pygame
import sys
import random
import time
from copy import deepcopy

from base_scene import BaseScene
from game_over_scene import GameOverScene
from piece import Piece, SHAPES, COLORS
from game_resources import IMAGES, SOUNDS

BOX_SIZE = 20 # how big each square is

X_MARGIN = 15
Y_MARGIN = 115 # padding between game board and SCREEN edge
BOARD_SIZE = (10, 20) # rows and columns of game board

BIG_FONT = pygame.font.Font('freesansbold.ttf', 25)
NORMAL_FONT = pygame.font.Font('freesansbold.ttf', 15)

BG_COLOR = (120, 120, 120)
BOARD_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)

MOVEMENT_FREQ = .2 # how quickly the player can move the pieces


def calculate_lvl_and_freq(score):
	level = int(score / 10) + 1
	fall_freq = .27 - (level * .02)
	return level, fall_freq


class GameScene(BaseScene):


	def __init__(self, board_size=BOARD_SIZE):
		super().__init__()

		pygame.mixer.music.load('assets/song.ogg')
		pygame.mixer.music.play(-1)

		# this array is for the blocks on the board
		self.board_width, self.board_height = board_size
		self.board = self.get_empty_board()

		self.last_move_down_time = time.time()
		self.last_move_sideways_time = time.time()
		self.last_fall_time = time.time()

		self.moving_down = False
		self.moving_left = False
		self.moving_right = False

		self.score = 0
		self.level, self.fall_freq = calculate_lvl_and_freq(self.score)

		self.next_piece = self.new_piece()
		self.falling_piece = self.new_piece()

		# buttons are the same space from the game board as the game board...
		# ... is from the edge of the screen
		button_x = (X_MARGIN * 2) + (BOX_SIZE * self.board_width)
		self.next_rect = pygame.Rect(button_x, (Y_MARGIN + 25), 100, 100)
		self.pause_rect = pygame.Rect(button_x, (25 + self.next_rect.bottomleft[1]), 100, 100)
		self.help_rect = pygame.Rect(button_x, (25 + self.pause_rect.bottomleft[1]), 100, 100)

		self.paused = False
		self.helping = False


	def to_pixel_coords(self, box_x, box_y):
		x = X_MARGIN + (box_x * BOX_SIZE)
		y = Y_MARGIN + (box_y * BOX_SIZE)
		return x, y


	def get_empty_board(self):
		return [[None for x in range(self.board_width)] for y in range(self.board_height)]


	def is_on_board(self, x, y):
		return 0 <= x < self.board_width and y < self.board_height


	def new_piece(self):
		# must initialize shape first
		# take shape input
		shape = Piece.to_array(random.choice(list(SHAPES.values())))
		color = random.choice(COLORS)
		return Piece(self, int(self.board_width / 2), -2, shape, color, BOX_SIZE)


	def process_inputs(self, events, pressed_keys):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.pause_rect.collidepoint(pygame.mouse.get_pos()) and not self.helping:
					self.paused = not self.paused
				elif self.help_rect.collidepoint(pygame.mouse.get_pos()):
					self.helping = not self.helping
					self.paused = self.helping
			elif event.type == pygame.KEYDOWN:
				k = event.key
				
				if k == pygame.K_p:
					# toggle pause
					self.paused = not self.paused
					
				# don't process keys if paused
				if self.paused or self.helping:
					return
				
				if k == pygame.K_UP:
					# rotate
					rotated = deepcopy(self.falling_piece)
					rotated.rotate()
					if self.is_valid_position(rotated):
						self.falling_piece = rotated
				elif k == pygame.K_DOWN:
					# move downwards faster
					self.moving_down = True
					if self.is_valid_position(self.falling_piece, adj_y=1):
						self.falling_piece.y += 1
					self.last_move_down_time = time.time()
				elif k == pygame.K_LEFT and self.is_valid_position(self.falling_piece, adj_x=-1):
					# move left
					self.falling_piece.x -= 1
					self.moving_left = True
					self.moving_right = False
					self.last_move_sideways_time = time.time()
				elif k == pygame.K_RIGHT and self.is_valid_position(self.falling_piece, adj_x=1):
					# move right
					self.falling_piece.x += 1
					self.moving_left = False
					self.moving_right = True
					self.last_move_sideways_time = time.time()
				elif k == pygame.K_SPACE:
					# drop to bottom
					self.moving_down = False
					self.moving_left = False
					self.moving_right = False
					y = 0
					for i in range(1, self.board_height):
						if not self.is_valid_position(self.falling_piece, adj_y=i):
							break
						y = i
					self.falling_piece.y += y
			elif event.type == pygame.KEYUP:
				k = event.key
				if k == pygame.K_LEFT:
					self.moving_left = False
				elif k == pygame.K_RIGHT:
					self.moving_right = False
				elif k == pygame.K_DOWN:
					self.moving_down = False


	def update(self):
		#don't update if paused
		if self.paused or self.helping:
			pygame.mixer.music.pause()
			return
		else:
			pygame.mixer.music.unpause()

		# do updating:
		# no more input, now for updating
		# user move it sideways
		if (self.moving_left or self.moving_right) and time.time() - self.last_move_sideways_time > MOVEMENT_FREQ:
			if self.moving_left and self.is_valid_position(self.falling_piece, adj_x=-1):
				self.falling_piece.x -= 1
			if self.moving_right and self.is_valid_position(self.falling_piece, adj_x=1):
				self.falling_piece.x += 1
			self.last_move_sideways_time = time.time()

		# user move down
		if self.moving_down and time.time() - self.last_move_down_time > MOVEMENT_FREQ and self.is_valid_position(self.falling_piece, adj_y=1):
			self.falling_piece.y += 1
			self.last_move_down_time = time.time()

		# natural fall`
		if time.time() - self.last_fall_time > self.fall_freq:
			# landed?
			if not self.is_valid_position(self.falling_piece, adj_y=1):
				self.add_to_board(self.falling_piece)
				# use list from removing lines to change score and animate
				removed_lines = self.remove_complete_lines()
				self.score += removed_lines
				self.level, self.fall_freq = calculate_lvl_and_freq(self.score)
				self.falling_piece = None
				# only play 1 sound
				if removed_lines:
					SOUNDS['break'].play()
				else:
					SOUNDS['rotate'].play()
			else:
				self.falling_piece.y += 1
				self.last_fall_time = time.time()

		# tick falling piece or detect lose
		if self.falling_piece is None:
			self.falling_piece = self.next_piece
			self.next_piece = self.new_piece()
			self.last_fall_time = time.time()

			# check top blocks to determine GAME OVER
			if not self.is_valid_position(self.falling_piece):
				self.switch_to_scene(GameOverScene(self.score, self.level, GameScene( (self.board_width, self.board_height) )))
				return
			for x in range(3, self.board_width-4):
				if self.board[0][x] is not None:
					self.switch_to_scene(GameOverScene(self.score, self.level, GameScene( (self.board_width, self.board_height) )))
					return


	def display(self, screen):
		# don't draw crucial game info if help or pause is shown
		self.draw_background(screen)
		self.draw_board(screen)
		self.draw_next_piece(screen)
		self.draw_buttons(screen)
		if self.falling_piece is not None and not (self.paused or self.helping): # there might not be a current falling piece
			self.falling_piece.draw(screen)
		self.draw_status(screen)

		if self.helping:
			self.show_help(screen)
		elif self.paused:
			self.show_pause(screen)


	def draw_buttons(self, screen):
		pygame.draw.rect(screen, (0, 0, 0), self.pause_rect, 5)
		pygame.draw.rect(screen, (125, 255, 0), self.pause_rect)
		surf = NORMAL_FONT.render('Pause', True, TEXT_COLOR)
		surf_rect = surf.get_rect()
		surf_rect.center = self.pause_rect.center
		screen.blit(surf, surf_rect)

		pygame.draw.rect(screen, (0, 0, 0), self.help_rect, 5)
		pygame.draw.rect(screen, (255, 125, 0), self.help_rect)
		surf = NORMAL_FONT.render('Help', True, TEXT_COLOR)
		surf_rect = surf.get_rect()
		surf_rect.center = self.help_rect.center
		screen.blit(surf, surf_rect)


	def draw_background(self, screen):
		screen.fill(BG_COLOR)
		screen.blit(IMAGES['title'], (0,0))


	def draw_box(self, screen, box_x, box_y, color, pixel_x=None, pixel_y=None, draw_blank=False):
		# pixel args override box coords
		if pixel_x is None and pixel_y is None:
			pixel_x, pixel_y = self.to_pixel_coords(box_x, box_y)
		the_rect = (pixel_x, pixel_y, BOX_SIZE, BOX_SIZE)
		if color is None:
			if draw_blank:
				pygame.draw.rect(screen, BOARD_COLOR, the_rect)
			else:
				return
		else:
			screen.blit(IMAGES[color+' brick'], the_rect)


	def draw_board(self, screen):
		# draw border
		pygame.draw.rect(screen, BORDER_COLOR, (X_MARGIN, Y_MARGIN, self.board_width*BOX_SIZE, self.board_height*BOX_SIZE), 5)
		# draw background
		pygame.draw.rect(screen, BOARD_COLOR, (X_MARGIN, Y_MARGIN, self.board_width*BOX_SIZE, self.board_height*BOX_SIZE))
		if self.paused or self.helping:
			return
		for x in range(self.board_width):
			for y in range(self.board_height):
				cell = self.board[y][x]
				self.draw_box(screen, x, y, cell)


	def add_to_board(self, piece):
		for x in range(piece.width):
			for y in range(piece.height):
				if piece.get_at(x, y) is not None:
					self.board[y + piece.y][x + piece.x] = piece.color


	def is_complete_line(self, y):
		for x in range(self.board_width):
			if self.board[y][x] is None:
				return False
		return True


	def remove_complete_lines(self):
		lines_removed = 0
		y = self.board_height - 1 # start from bottom
		while y >= 0:
			if self.is_complete_line(y):
				lines_removed += 1
				for pull_down_y in range(y, 0, -1):
					for x in range(self.board_width):
						self.board[pull_down_y][x] = self.board[pull_down_y-1][x]
				# clear top line
				for x in range(self.board_width):
					self.board[0][x] = None
			else:
				y -= 1
		return lines_removed


	def is_valid_position(self, piece, adj_x=0, adj_y=0):
		for x in range(piece.width):
			for y in range(piece.height):
				is_above_board = y + piece.y + adj_y < 0
				if is_above_board or piece.get_at(x, y) is None:
					continue
				if not self.is_on_board(x + piece.x + adj_x, y + piece.y + adj_y):
					return False
				if self.board[y + piece.y + adj_y][x + piece.x + adj_x] is not None:
					return False
		return True


	def draw_status(self, screen):
		score_surf = NORMAL_FONT.render("Score: %s"%self.score, True, TEXT_COLOR)
		score_rect = score_surf.get_rect()
		score_rect.bottomleft = (X_MARGIN, Y_MARGIN-5)
		screen.blit(score_surf, score_rect)

		level_surf = NORMAL_FONT.render("Level: %s"%self.level, True, TEXT_COLOR)
		level_rect = level_surf.get_rect()
		level_rect.bottomleft = (2*X_MARGIN+BOX_SIZE*self.board_width, Y_MARGIN-5)
		screen.blit(level_surf, level_rect)


	def draw_next_piece(self, screen):
		next_area = self.next_rect
		pygame.draw.rect(screen, BORDER_COLOR, next_area, 5)
		pygame.draw.rect(screen, BOARD_COLOR, next_area)

		surf = NORMAL_FONT.render("Next:", True, TEXT_COLOR)
		rect = surf.get_rect()
		rect.topleft = (next_area.topleft[0], next_area.topleft[1]-25)
		screen.blit(surf, rect)

		# dont draw next piece if not playing
		if self.paused or self.helping:
			return
		center_x = BOX_SIZE * self.next_piece.width / 2
		center_y = BOX_SIZE * self.next_piece.height / 2
		self.next_piece.draw(screen, pixel_x=next_area.center[0]-center_x, pixel_y=next_area.center[1]-center_y)


	def show_pause(self, screen):
		screen_height = screen.get_rect().height
		surf = BIG_FONT.render("PAUSED", True, TEXT_COLOR)
		surf_rect = surf.get_rect()
		surf_rect.center = (X_MARGIN+(BOX_SIZE*self.board_width/2), screen_height/2)
		screen.blit(surf, surf_rect)


	def show_help(self, screen):
		screen_height = screen.get_rect().height
		x = X_MARGIN + (BOX_SIZE * self.board_width / 2)
		y = screen_height/2
		surf = BIG_FONT.render("HELP", True, TEXT_COLOR)
		surf_rect = surf.get_rect()
		surf_rect.center = (x, y)
		screen.blit(surf, surf_rect)

		for i, text in enumerate(['Move piece = Arrow keys', 'Rotate piece = Up arrow key', 'Drop piece = Space key']):
			surf = NORMAL_FONT.render(text, True, TEXT_COLOR)
			surf_rect = surf.get_rect()
			surf_rect.center = (x, y + (i+1)*30)
			screen.blit(surf, surf_rect)