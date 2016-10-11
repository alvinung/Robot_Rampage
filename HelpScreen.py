# -*- coding: utf-8 -*-
"""

@author: Alvin
"""

import pygame
from pygame.locals import *

class HelpScreen:
    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.Surface(screen.get_size())
        pygame.draw.rect(self.background, (50, 50, 50), self.background.get_rect())
        self.font = pygame.font.Font(None, 35)
        self.HelpFont = pygame.font.Font(None, 80)
        self.HelpText = self.HelpFont.render("Help Screen", 1, (255,255,255))
        for i, txt in enumerate(
            ("",
             "",
             "",
             "Game Background:",
             "Chrono was a brilliant scientist from Hallow's End, known throughout for his magnificent robot creations.",
             "In the year 3007, a mysterious plague struck the land, turning everyone he had ever known into Heartless.",
             "They are vile creatures determined to bring about the destruction of the Earth. Luckily, Chrono was experimenting",
             "with his new Mk-8000 super human suit at the time, which protected him from the transformation. ",
             "Now armed with his new state of the art battle suit, he has only one goal. To take on the endless onslaught of",
             "the Heathless and defend what is left of his lonely world.",
             "",
             "Controls: [W] -->  Move Left",
             "                   [E] -->  Move Right",
             "          [O] -->  Shoot",
             "[SPACE] --> Jump",
             "",
             "*** Cheat Input ***",
             "Press [J] + [K] + [L] simultaniously",
             "for invincibility")):
            self.textout(txt, 100 + i * 50)
            
    def textout(self, text, y):
        rText = self.font.render(text, 1, (255, 255, 255))
        textRec = rText.get_rect()
        textRec.centerx = self.background.get_rect().centerx
        textRec .centery = y
        self.background.blit(rText, textRec)
        
    def run(self, events):
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.HelpText, (680, 100))
        pygame.display.flip()
