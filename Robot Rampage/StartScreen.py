# -*- coding: utf-8 -*-
"""

@author: Alvin
"""

import pygame
from pygame.locals import *

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.Surface(screen.get_size())
        pygame.draw.rect(self.background, (50, 50, 50), self.background.get_rect())
        self.font = pygame.font.Font(None, 60)
        self.titleFont = pygame.font.Font(None, 200)
        self.titleText = self.titleFont.render("ROBOT RAMPAGE", 1, (255,255,255))
        self.enterText = self.font.render("Press \"Enter\" to Start", 1, (255,255,255))
        self.helpText = self.font.render("Press \"F1\" for Help", 1, (255,255,255))
        
    def run(self, events):
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.titleText, (240, 100))
        self.screen.blit(self.enterText, (640, 800))
        self.screen.blit(self.helpText, (670, 850))
        pygame.display.flip()
