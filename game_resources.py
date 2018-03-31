#!/usr/bin/env python3

import pygame

IMAGES = ['title', 'red brick', 'blue brick', 'green brick', 'white brick', 'black brick']
IMAGES = {x: pygame.image.load('assets/%s.png'%x) for x in IMAGES}

SOUNDS = ['over', 'rotate', 'select', 'break']
SOUNDS = {x: pygame.mixer.Sound('assets/%s.ogg'%x) for x in SOUNDS}
