#!/usr/bin/env python3
#TODO: fix the row animation

import pygame
import sys
import random
import time
from copy import deepcopy

BOX_SIZE = 20 # how big each square is
SCREEN_WIDTH, SCREEN_HEIGHT = (350, 530)
X_MARGIN, Y_MARGIN = (15, 115) # padding between game board and SCREEN edge
BOARD_WIDTH, BOARD_HEIGHT = (10, 20) # rows and columns of game board
BG_COLOR = (120, 120, 120)
BOARD_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
MOVEMENT_FREQ = .2 # how quickly the player can move the pieces
FPS = 30
COLORS = ['red', 'blue', 'white', 'black', 'green'] # also used for filenames
SOUNDS = ['break', 'over', 'rotate', 'select']
# o = block, / = next row, _ = blank
SHAPES = {
	'O': 'oo/oo',
	'J': 'o/ooo',
	'L': 'ooo/o',
	'I': 'oooo',
	'S': '_oo/oo',
	'Z': 'oo/_oo',
	'T': 'ooo/_o',
	'*': 'o'
}
NEXT_RECT = pygame.Rect(X_MARGIN*2+BOX_SIZE*BOARD_WIDTH, Y_MARGIN+25, 100, 100)
PAUSE_RECT = pygame.Rect(X_MARGIN*2+BOX_SIZE*BOARD_WIDTH, Y_MARGIN+25*2+NEXT_RECT.height, 100, 100)
HELP_RECT = pygame.Rect(X_MARGIN*2+BOX_SIZE*BOARD_WIDTH, 25+PAUSE_RECT.bottomleft[1], 100, 100)


def terminate():
	pygame.quit()
	sys.exit()
	
	
class Piece:

	@staticmethod
	def to_array(shape_string):
		rows = shape_string.split('/')
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
					if value == '_':
						continue
					else:
						arr[y][x] = 'o'
		return arr
		
	# x, y on board, shape is either string or shape key
	def __init__(self, x=None, y=-2, shape=None, color=None):
		# must initialize shape first
		# take shape input
		if shape is None:
			self.shape = random.choice(list(SHAPES.values()))
		else:
			if shape in list(SHAPES.keys()):
				self.shape = SHAPES[shape]
			else:
				self.shape = shape
		# convert shape string to array
		if isinstance(self.shape, str):
			self.shape = self.to_array(self.shape)
			
		if x is None:
			self.x = int(BOARD_WIDTH / 2) - int(self.width / 2)
		else:
			self.x = x
			
		self.y = y
			
		if color is None:
			self.color = random.choice(COLORS)
		else:
			self.color = color
		
	def rotate(self):
		# some explain: convert zip to list and each tuple inside to list
		center = (self.width//2, self.height//2)
		self.shape = list(list(x) for x in zip(*reversed(self.shape)))
		new_center = (self.width//2, self.height//2)
		self.x -= new_center[0] - center[0]
		self.y -= new_center[1] - center[1]
		return self
		
	def is_valid_index(self, x, y):
		if self.get_at(x, y):
			return True
		return False
			
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
			
	def draw(self, pixel_x=None, pixel_y=None):
		if pixel_x is None and pixel_y is None:
			pixel_x, pixel_y = to_pixel_coords(self.x, self.y)
		for x in range(self.width):
			for y in range(self.height):
				value = self.get_at(x, y)
				if value:
					draw_box(None, None, self.color, pixel_x + (BOX_SIZE*x), pixel_y + (BOX_SIZE*y))
			
	def __str__(self):
		return str(self.shape)
		
	def __repr__(self):
		return 'Piece(x=%s, y=%s, shape=%s, rotation=%s, color=%s)'%(self.x, self.y, self.shape, self.rotation, self.color)

		
def draw_buttons():
	pygame.draw.rect(SCREEN, (0, 0, 0), PAUSE_RECT, 5)
	pygame.draw.rect(SCREEN, (125, 255, 0), PAUSE_RECT)
	surf = NORMAL_FONT.render('Pause', True, TEXT_COLOR)
	surf_rect = surf.get_rect()
	surf_rect.center = PAUSE_RECT.center
	SCREEN.blit(surf, surf_rect)
	
	pygame.draw.rect(SCREEN, (0, 0, 0), HELP_RECT, 5)
	pygame.draw.rect(SCREEN, (255, 125, 0), HELP_RECT)
	surf = NORMAL_FONT.render('Help', True, TEXT_COLOR)
	surf_rect = surf.get_rect()
	surf_rect.center = HELP_RECT.center
	SCREEN.blit(surf, surf_rect)
	
	
def wait_for_keypress():
	while True:
		if check_for_keypress():
			return
				
				
def check_for_keypress():
	for event in pygame.event.get([pygame.KEYUP, pygame.KEYDOWN]):
		if event.type == pygame.QUIT:
			terminate()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				terminate()
			continue
		return event.key
	return None
			
			
def draw_background():
	SCREEN.fill(BG_COLOR)
	SCREEN.blit(IMAGES['title'], (0,0))
	
	
# run one round of brick game
def run_game():
	board = get_empty_board()
	
	last_move_down_time = time.time()
	last_move_sideways_time = time.time()
	last_fall_time = time.time()

	moving_down = False
	moving_left = False
	moving_right = False

	score = 0
	level, fall_freq = calculate_lvl_and_freq(score)

	next_piece = Piece()
	falling_piece = Piece()
	
	paused = False
	helping = False
	
	while True:
		# events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				terminate()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if PAUSE_RECT.collidepoint(pygame.mouse.get_pos()) and not helping:
					paused = not paused
				elif HELP_RECT.collidepoint(pygame.mouse.get_pos()):
					helping = not helping
					paused = helping
			elif event.type == pygame.KEYDOWN:
				k = event.key
				if k == pygame.K_ESCAPE:
					terminate()
				if k == pygame.K_p:
					# toggle pause
					paused = not paused
				if k == pygame.K_UP:
					# rotate
					rotated = deepcopy(falling_piece)
					rotated.rotate()
					if is_valid_position(board, rotated):
						falling_piece = rotated
				elif k == pygame.K_DOWN:
					# move downwards faster
					moving_down = True
					if is_valid_position(board, falling_piece, adj_y=1):
						falling_piece.y += 1
					last_move_down_time = time.time()
				elif k == pygame.K_LEFT and is_valid_position(board, falling_piece, adj_x=-1):
					# move left
					falling_piece.x -= 1
					moving_left = True
					moving_right = False
					last_move_sideways_time = time.time()
				elif k == pygame.K_RIGHT and is_valid_position(board, falling_piece, adj_x=1):
					# move right
					falling_piece.x += 1
					moving_left = False
					moving_right = True
					last_move_sideways_time = time.time()
				elif k == pygame.K_SPACE:
					# drop to bottom
					moving_down = False
					moving_left = False
					moving_right = False
					y = 0
					for i in range(1, BOARD_HEIGHT):
						if not is_valid_position(board, falling_piece, adj_y=i):
							break
						y = i
					falling_piece.y += y
			elif event.type == pygame.KEYUP:
				k = event.key
				if k == pygame.K_LEFT:
					moving_left = False
				elif k == pygame.K_RIGHT:
					moving_right = False
				elif k == pygame.K_DOWN:
					moving_down = False

		#don't update if paused
		hide_info = paused or helping
		
		# do updating:
		# no more input, now for updating
		# user move it sideways
		if not hide_info:
			pygame.mixer.music.unpause()
			if (moving_left or moving_right) and time.time() - last_move_sideways_time > MOVEMENT_FREQ:
				if moving_left and is_valid_position(board, falling_piece, adj_x=-1):
					falling_piece.x -= 1
				if moving_right and is_valid_position(board, falling_piece, adj_x=1):
					falling_piece.x += 1
				last_move_sideways_time = time.time()

			# user move down
			if moving_down and time.time() - last_move_down_time > MOVEMENT_FREQ and is_valid_position(board, falling_piece, adj_y=1):
				falling_piece.y += 1
				last_move_down_time = time.time()

			# natural fall`
			if time.time() - last_fall_time > fall_freq:
				# landed?
				if not is_valid_position(board, falling_piece, adj_y=1):
					add_to_board(board, falling_piece)
					# use list from removing lines to change score and animate
					removed_lines = remove_complete_lines(board)
					score += removed_lines
					level, fall_freq = calculate_lvl_and_freq(score)
					falling_piece = None
				else:
					falling_piece.y += 1
					last_fall_time = time.time()

			# tick falling piece or detect lose
			if falling_piece is None:
				falling_piece = next_piece
				next_piece = Piece()
				last_fall_time = time.time()
				
				# check top blocks to determine GAME OVER
				if not is_valid_position(board, falling_piece):
					return (level, score)
				for x in range(3, BOARD_WIDTH-4):
					if board[0][x] is not None:
						return (level, score)
		else:
			pygame.mixer.music.pause()

		# display, but don't draw crucial game info if help or pause is shown
		draw_background()
		draw_board(board, hide_info)
		draw_next_piece(next_piece, hide_info)
		draw_buttons()
		if falling_piece is not None and not hide_info: # there might not be a current falling piece
			falling_piece.draw()
		draw_status(score, level)
		
		if helping:
			show_help()
		elif paused:
			show_pause()
			
		pygame.display.flip()
		FPS_CLOCK.tick(FPS)
		
	
def show_game_over():
	surf = BIG_FONT.render('GAME OVER', True, (0, 0, 255))
	surf_rect = surf.get_rect()
	surf_rect.center = (X_MARGIN + (BOX_SIZE * BOARD_WIDTH / 2), SCREEN_HEIGHT / 2)
	SCREEN.blit(surf, surf_rect)
	surf = BIG_FONT.render('GAME OVER', True, TEXT_COLOR)
	surf_rect = surf.get_rect()
	surf_rect.center = (2 + X_MARGIN + (BOX_SIZE * BOARD_WIDTH / 2), 2 + SCREEN_HEIGHT / 2)
	SCREEN.blit(surf, surf_rect)
	
	
def to_pixel_coords(box_x, box_y):
	x = X_MARGIN + (box_x * BOX_SIZE)
	y = Y_MARGIN + (box_y * BOX_SIZE)
	return x, y

	
def draw_box(box_x, box_y, color, pixel_x=None, pixel_y=None, draw_blank=False):
	# pixel args override box coords
	if pixel_x is None and pixel_y is None:
		pixel_x, pixel_y = to_pixel_coords(box_x, box_y)
	the_rect = (pixel_x, pixel_y, BOX_SIZE, BOX_SIZE)
	if color is None:
		if draw_blank:
			pygame.draw.rect(SCREEN, BOARD_COLOR, the_rect)
		else:
			return
	else:
		SCREEN.blit(IMAGES[color], the_rect)

		
def draw_board(board, hide_info=False):
	# draw border
	pygame.draw.rect(SCREEN, BORDER_COLOR, (X_MARGIN, Y_MARGIN, BOARD_WIDTH*BOX_SIZE, BOARD_HEIGHT*BOX_SIZE), 5)
	# draw background
	pygame.draw.rect(SCREEN, BOARD_COLOR, (X_MARGIN, Y_MARGIN, BOARD_WIDTH*BOX_SIZE, BOARD_HEIGHT*BOX_SIZE))
	if hide_info:
		return
	for x in range(BOARD_WIDTH):
		for y in range(BOARD_HEIGHT):
			cell = board[y][x]
			draw_box(x, y, cell)

			
def get_empty_board():
	return [[None for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]

	
def is_on_board(x, y):
	return 0 <= x < BOARD_WIDTH and y < BOARD_HEIGHT

	
def add_to_board(board, piece):
	for x in range(piece.width):
		for y in range(piece.height):
			if piece.get_at(x, y) is not None:
				board[y + piece.y][x + piece.x] = piece.color

				
def calculate_lvl_and_freq(score):
	level = int(score / 10) + 1
	fall_freq = .27 - (level * .02)
	return level, fall_freq

	
def is_complete_line(board, y):
	for x in range(BOARD_WIDTH):
		if board[y][x] is None:
			return False
	return True

	
def remove_complete_lines(board):
	lines_removed = 0
	y = BOARD_HEIGHT - 1 # start from bottom
	while y >= 0:
		if is_complete_line(board, y):
			lines_removed += 1
			for pull_down_y in range(y, 0, -1):
				for x in range(BOARD_WIDTH):
					board[pull_down_y][x] = board[pull_down_y-1][x]
			# clear top line
			for x in range(BOARD_WIDTH):
				board[0][x] = None
		else:
			y -= 1
	if lines_removed > 0:
		SOUNDS['break'].play()
	else:
		SOUNDS['rotate'].play()
	return lines_removed

	
def is_valid_position(board, piece, adj_x=0, adj_y=0):
	for x in range(piece.width):
		for y in range(piece.height):
			is_above_board = y + piece.y + adj_y < 0
			if is_above_board or piece.get_at(x, y) is None:
				continue
			if not is_on_board(x + piece.x + adj_x, y + piece.y + adj_y):
				return False
			if board[y + piece.y + adj_y][x + piece.x + adj_x] is not None:
				return False
	return True

	
def draw_status(score, level):
	score_surf = NORMAL_FONT.render("Score: %s"%score, True, TEXT_COLOR)
	score_rect = score_surf.get_rect()
	score_rect.bottomleft = (X_MARGIN, Y_MARGIN-5)
	SCREEN.blit(score_surf, score_rect)

	level_surf = NORMAL_FONT.render("Level: %s"%level, True, TEXT_COLOR)
	level_rect = level_surf.get_rect()
	level_rect.bottomleft = (2*X_MARGIN+BOX_SIZE*BOARD_WIDTH, Y_MARGIN-5)
	SCREEN.blit(level_surf, level_rect)

	
def draw_next_piece(next_piece, hide_info=False):
	next_area = NEXT_RECT
	pygame.draw.rect(SCREEN, BORDER_COLOR, next_area, 5)
	pygame.draw.rect(SCREEN, BOARD_COLOR, next_area)
	
	surf = NORMAL_FONT.render("Next:", True, TEXT_COLOR)
	rect = surf.get_rect()
	rect.topleft = (next_area.topleft[0], next_area.topleft[1]-25)
	SCREEN.blit(surf, rect)
	
	if hide_info:
		return
	center_x = BOX_SIZE * next_piece.width / 2
	center_y = BOX_SIZE * next_piece.height / 2
	next_piece.draw(pixel_x=next_area.center[0]-center_x, pixel_y=next_area.center[1]-center_y)
	
		
def show_pause():
	surf = BIG_FONT.render("PAUSED", True, TEXT_COLOR)
	surf_rect = surf.get_rect()
	surf_rect.center = (X_MARGIN+(BOX_SIZE*BOARD_WIDTH/2), SCREEN_HEIGHT/2)
	SCREEN.blit(surf, surf_rect)
	
	
def show_help():
	x = X_MARGIN + (BOX_SIZE * BOARD_WIDTH / 2)
	y = SCREEN_HEIGHT/2
	surf = BIG_FONT.render("HELP", True, TEXT_COLOR)
	surf_rect = surf.get_rect()
	surf_rect.center = (x, y)
	SCREEN.blit(surf, surf_rect)
	
	for i, text in enumerate(['Move piece = Arrow keys', 'Rotate piece = Up arrow key', 'Drop piece = Space key']):
		surf = NORMAL_FONT.render(text, True, TEXT_COLOR)
		surf_rect = surf.get_rect()
		surf_rect.center = (x, y + (i+1)*30)
		SCREEN.blit(surf, surf_rect)	
	

def main():
	global BIG_FONT, NORMAL_FONT, SCREEN, IMAGES, FPS_CLOCK, SOUNDS
	pygame.init()
	SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Raining Bricks")
	FPS_CLOCK = pygame.time.Clock()
	
	# load necessary details
	NORMAL_FONT = pygame.font.Font('freesansbold.ttf', 15)
	BIG_FONT = pygame.font.Font('freesansbold.ttf', 25)
	# load images from color list
	IMAGES = {x: pygame.image.load('assets/%s brick.png'%x) for x in COLORS}
	IMAGES['title'] = pygame.image.load('assets/title.png')
	# load sounds in a similar way
	SOUNDS = {x: pygame.mixer.Sound('assets/%s.ogg'%x) for x in SOUNDS}
	for s in SOUNDS.values():
		s.set_volume(.25)

	while True:
		# play music until g.o.
		pygame.mixer.music.load('assets/song.mid')
		pygame.mixer.music.play(-1)
		level, score = run_game() # get level and score for game over screen
		pygame.mixer.music.stop()
		SOUNDS['over'].play()
		show_game_over()
		pygame.display.update()
		time.sleep(3)


if __name__ == '__main__':
	main()
