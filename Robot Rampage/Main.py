# -*- coding: utf-8 -*-
"""

@author: Alvin
"""

import pygame
from pygame.locals import *
from StartScreen import StartScreen
from HelpScreen import HelpScreen
from GameRoom import GameRoom

screenSize = (1680, 1050)
global FPS
FPS = 30
def main():
    pygame.init()
    screen = pygame.display.set_mode(screenSize)
    screenRect = screen.get_rect()
    
    #Loading Screen
    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("Loading...", 1, (50, 100, 150))
        textRec = text.get_rect()
        textRec.center = screen.get_rect().center
        screen.blit(text, textRec)
    pygame.display.flip()
    
    clock = pygame.time.Clock()
    clock.tick(1)
    
    #Creates resources
    start_screen = StartScreen(screen)
    help_screen = HelpScreen(screen)
    game_screen = GameRoom(screen)
    
    current_screen = start_screen
    prev_screen = start_screen
    
    while 1: 
        clock.tick(30)
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if current_screen == help_screen:
                    if event.key == K_F1:
                        current_screen = prev_screen
                elif event.key == K_ESCAPE:
                    return
                elif event.key == K_F1:
                    prev_screen = current_screen
                    current_screen = help_screen
                elif event.key == K_RETURN:
                    current_screen = game_screen
                    prev_screen = help_screen
        
        current_screen.run(events)
        
if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
