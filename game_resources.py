import pygame
import os

IMAGES = ['title', 'cloud', 'red brick', 'blue brick', 'green brick', 'white brick', 'black brick', 'orange brick']
SOUNDS = ['over', 'rotate', 'select', 'break']

current = os.getcwd()
IMAGES = {x: pygame.image.load(os.path.join(current, 'assets', f'{x}.png')) for x in IMAGES}
SOUNDS = {x: pygame.mixer.Sound(os.path.join(current, 'assets', f'{x}.wav')) for x in SOUNDS}
for s in SOUNDS.values():
	s.set_volume(.5)
