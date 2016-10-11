# -*- coding: utf-8 -*-
"""

@author: Alvin
"""

import pygame, os, sys
from pygame.locals import *
from random import randint, random
from math import sin, cos, pi
import numpy as N

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

SCREEN_SIZE = (1680, 1050) #resolution of the game
global HORIZ_MOV_INCR
HORIZ_MOV_INCR = 10 #speed of movement
global clock

class DepthUpdates(pygame.sprite.RenderUpdates):
    """A sprite group that renders sprites in y-coordinate order.
       Useful for isometric and other pseudo-3d games where things
       can walk behind and in front of others."""

    def sprites(self):
        spr = pygame.sprite.RenderUpdates.sprites(self)
        spr.sort(key=lambda s:s.rect.bottom)
        return spr

class LoadImages:
    def __init__(self):
        self.dict = {}
        width = 32
        surf = pygame.Surface((width, width))
        r = surf.get_rect()

    def get(self, name):
        return self.dict[name]

    def load_image(self, name, colorkey=None):
        # Loads and returns a single image file
        dictname = name[0:name.find('.')]
        fullname = os.path.join('Data', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print (('Cannot load image:', fullname))
            raise SystemExit(message)
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, RLEACCEL)
        self.dict[dictname] = image, image.get_rect()

    def load_strip(self, name, width, height, colorkey=None):
        # Loads images as strips
        dictname = name[0:name.find('.')]
        self.load_image(name, colorkey)
        image, rect = self.dict[dictname]
        images = []
        for y in range(0, image.get_height(), height):
            for x in range(0, image.get_width(), width):
                newimage = pygame.Surface((width, height))
                newimage.blit(image, (0,0), pygame.Rect(x, y, width, height))
                newimage.convert()
                if colorkey is not None:
                    if colorkey is -1:
                        colorkey = newimage.get_at((0, 0))
                    newimage.set_colorkey(colorkey, RLEACCEL)
                images.append(newimage)
        self.dict[dictname] = images, images[0].get_rect()

class LoadSounds:
    def __init__(self):
        self.dict = {}
            
    def get(self,name):
        return self.dict[name]
    
    def load_sound(self, name):
        """Loads a sound from a file."""
        class NoneSound:
            def play(self): pass
        if not pygame.mixer or not pygame.mixer.get_init():
            sound = NoneSound()
        else:
            fullname = os.path.join('Data', name)
            try:
                sound = pygame.mixer.Sound(fullname)
            except pygame.error as message:
                print (('Cannot load sound:', fullname))
                raise SystemExit( message)
        dictname = name[0:name.find('.')]
        self.dict[dictname] = sound

def bounce(sp1, sp2):
    hdist = sp1.rect.left - sp2.rect.left
    vdist = sp1.rect.top - sp2.rect.top
    if abs(hdist) > abs(vdist):
        if hdist < 0:
            sp1.hspeed = -abs(sp1.hspeed)
        else:
            sp1.hspeed = abs(sp1.hspeed)
    else:
        if vdist < 0:
            sp1.vspeed = -abs(sp1.vspeed)
        else:
            sp1.vspeed = abs(sp1.vspeed)

def hit(sp1, sp2):
    sp1Rect = sp1.get_rect()
    sp2Rect = sp2.get_rect()
    if hdist < 0 and vdist < 0:
        sp1.kill()
        sp2.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, Images, Sounds):
        pygame.sprite.Sprite.__init__(self)
        Sounds.get('explosion').play()
        self.images,self.rect = Images.get('explosion')
        self.rect.centerx = x
        self.rect.centery = y
        self.nframes = len(self.images)
        self.frame = 0
        self.image = self.images[self.frame]
        self.aspeed = 0.5

    def update(self):
        if self.frame >= self.nframes:
            self.kill()
        else:
            self.image = self.images[int(self.frame)]

class Ghost(pygame.sprite.Sprite):
    # Moves ghost around the screen
    def __init__(self, Images, screensize, Sprites, Sounds):
        pygame.sprite.Sprite.__init__(self)
        self.images_right, self.rect = Images.get('ghost_right')
        self.images_left, self.rect = Images.get('ghost_left')
        self.frame = 0
        self.aspeed = 0.5 + random()
        self.nframes = len(self.images_right)
        direction = randint(110, 260)
        if (direction >= 90 and direction <= 270):
            self.images = self.images_left[self.frame]
        if (direction >= 0 and direction <= 90) or (direction >= 270 and direction <= 359):
            self.images = self.images_right[self.frame]
        self.image = self.images
        angle = pi * direction/180.0
        speed = randint(5, 10)
        self.hspeed = speed * cos(angle)
        self.vspeed = speed * sin(angle)
        self.rect = self.rect.move(randint(32, screensize[0] - 32*2), randint(32, screensize[1] - 32 * 2))
        self.Sprites = Sprites
        self.Images = Images
        self.Sounds = Sounds

    def update(self):
        # Move Ghost based on speed and direction
        self.rect = self.rect.move(self.hspeed, self.vspeed)
        self.frame = (self.aspeed + self.frame)
        while self.frame >= self.nframes:
            self.frame -= self.nframes
        self.image = self.images

    def kill(self):
        self.Sprites.add(Explosion(self.rect.centerx, self.rect.centery, self.Images, self.Sounds))
        pygame.sprite.Sprite.kill(self)

def RelRect(actor, camera):
    return pygame.Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

class Camera(object):
    '''Class for center screen on the player'''
    def __init__(self, screen, player, level_width, level_height):
        self.player = player
        self.rect = screen.get_rect()
        self.rect.center = self.player.center
        self.world_rect = Rect(0, 0, level_width, level_height)

    def update(self):
      if self.player.centerx > self.rect.centerx + 25:
          self.rect.centerx = self.player.centerx - 25
      if self.player.centerx < self.rect.centerx - 25:
          self.rect.centerx = self.player.centerx + 25
      if self.player.centery > self.rect.centery + 25:
          self.rect.centery = self.player.centery - 25
      if self.player.centery < self.rect.centery - 25:
          self.rect.centery = self.player.centery + 25
      self.rect.clamp_ip(self.world_rect)

    def draw_sprites(self, surf, sprites):
        for s in sprites:
            if s.rect.colliderect(self.rect):
                surf.blit(s.image, RelRect(s, self))

_xsteps = (1.0, 0.0, -1.0,  0.0)
_ysteps = (0.0, -1.0, 0.0,  1.0)
_steps = [N.array((x,y)) for x,y in zip(_xsteps, _ysteps)]

class projectile(pygame.sprite.Sprite):
    def __init__(self, shooter):
        self.shooter = shooter
        self.direction = shooter.direction 
        pygame.sprite.Sprite.__init__(self)
        if(self.direction == "right"):
            self.direction = 0
            self.x = shooter.rect.x + shooter.rect.width
            self.y = shooter.rect.centery
            self.image = pygame.image.load("Robot_Actions/right_shot.png").convert()
        elif(self.direction == "left"):
            self.direction = 2
            self.x = shooter.rect.x
            self.y = shooter.rect.centery
            self.image = pygame.image.load("Robot_Actions/left_shot.png").convert()
        self.pos = (self.x,self.y)
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]
        self.collisionRect = pygame.Rect(0,0,self.rect.width,self.rect.height)
        self.collisionRect.centerx = self.rect.centerx
        self.collisionRect.centery = self.rect.centery
        self.speed = 8
        self.damage = 10
        
    def update(self):
        self.pos += self.speed * _steps[self.direction]
        self.rect.center = tuple(N.round(self.pos))

class Robo(pygame.sprite.Sprite):
    '''class for player and collision'''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.canShoot = True
        self.MAX_SHOT_TIME = 10
        self.shotTimer = 0
        self.movy = 0
        self.movx = 0
        self.x = x
        self.y = y
        self.contact = False
        self.jump = False
        self.image = pygame.image.load('Robot_Actions/right_idle_01.png').convert()
        self.rect = self.image.get_rect()
        self.run_left = ["Robot_Actions/left_walk_01.png", "Robot_Actions/left_walk_02.png",
                        "Robot_Actions/left_walk_03.png", "Robot_Actions/left_walk_04.png"]
        self.run_right = ["Robot_Actions/right_walk_01.png", "Robot_Actions/right_walk_02.png",
                         "Robot_Actions/right_walk_03.png", "Robot_Actions/right_walk_04.png"]

        self.direction = "right"
        self.rect.topleft = [x, y]
        self.frame = 0
        self.projectiles = DepthUpdates()

    def getProjectiles(self):
        return self.projectiles

    def update(self, up, left, right, shoot, world):
        self.projectiles = DepthUpdates()
        if up:
            if self.contact:
                if self.direction == "right":
                    self.image = pygame.image.load("Robot_Actions/right_jump_03.png")
                else:
                    self.image = pygame.image.load("Robot_Actions/left_jump_03.png")
                self.jump = True
                self.movy -= 20

        if left:
            self.direction = "left"
            self.movx = -HORIZ_MOV_INCR
            if self.contact:
                self.frame += 1
                self.image = pygame.image.load(self.run_left[self.frame]).convert_alpha()
                if self.frame == 3: self.frame = 0
                if shoot and self.canShoot:
                    self.image = pygame.image.load("Robot_Actions/left_shoot_01.png").convert_alpha()
                    a = projectile(self)
                    self.projectiles.add(a)
                    self.canShoot = False
            else:
                self.image = self.image = pygame.image.load("Robot_Actions/left_jump_03.png").convert_alpha()
                if shoot and self.canShoot:
                    self.image = pygame.image.load("Robot_Actions/left_shoot_01.png").convert_alpha()
                    a = projectile(self)
                    self.projectiles.add(a)
                    self.canShoot = False

        if right:
            self.direction = "right"
            self.movx = +HORIZ_MOV_INCR
            if self.contact:
                self.frame += 1
                self.image = pygame.image.load(self.run_right[self.frame]).convert_alpha()
                if self.frame == 3: self.frame = 0
                if shoot and self.canShoot:
                    self.image = pygame.image.load("Robot_Actions/right_shoot_01.png").convert_alpha()
                    a = projectile(self)
                    self.projectiles.add(a)
                    self.canShoot = False
            else:
                self.image = self.image = pygame.image.load("Robot_Actions/right_jump_03.png").convert_alpha()
                if shoot and self.canShoot:
                    self.image = pygame.image.load("Robot_Actions/right_shoot_01.png").convert_alpha()
                    a = projectile(self)
                    self.projectiles.add(a)
                    self.canShoot = False

        if not (left or right):
            if not up and self.direction == "right":
                self.image = pygame.image.load("Robot_Actions/right_idle_01.png").convert_alpha()
                self.image.set_colorkey(self.image.get_at((0,0)))
            if not up and self.direction == "left":
                self.image = pygame.image.load("Robot_Actions/left_idle_01.png").convert_alpha()
            self.movx = 0
            if shoot and self.direction == "right" and self.canShoot:
                self.image = pygame.image.load("Robot_Actions/right_shoot_01.png").convert_alpha()
                a = projectile(self)
                self.projectiles.add(a)
                self.canShoot = False
            if shoot and self.direction == "left" and self.canShoot:
                self.image = pygame.image.load("Robot_Actions/left_shoot_01.png").convert_alpha()
                a = projectile(self)
                self.projectiles.add(a)
                self.canShoot = False
        self.rect.right += self.movx

        self.collide(self.movx, 0, world)


        if not self.contact:
            self.movy += 0.3
            if self.movy > 10:
                self.movy = 10
            self.rect.top += self.movy

        if self.jump:
            self.movy += 2
            self.rect.top += self.movy
            if self.contact == True:
                self.jump = False

        self.contact = False
        self.collide(0, self.movy, world)

        super(Robo, self).update()
        
        self.shotTimer += 1
        if self.shotTimer == self.MAX_SHOT_TIME:
            self.shotTimer = 0
            self.canShoot = True

    def collide(self, movx, movy, world):
        self.contact = False
        for o in world:
            if self.rect.colliderect(o):
                if movx > 0:
                    self.rect.right = o.rect.left
                if movx < 0:
                    self.rect.left = o.rect.right
                if movy > 0:
                    self.rect.bottom = o.rect.top
                    self.movy = 0
                    self.contact = True
                if movy < 0:
                    self.rect.top = o.rect.bottom
                    self.movy = 0  


class Level(object):
    '''Read a map and create a level'''
    def __init__(self, open_level):
        self.level1 = []
        self.world = []
        self.all_sprite = pygame.sprite.Group()
        self.level = open(open_level, "r")

    def create_level(self, x, y):
        for l in self.level:
            self.level1.append(l)

        for row in self.level1:
            for col in row:
                if col == "X":
                    obstacle = Obstacle(x, y)
                    self.world.append(obstacle)
                    self.all_sprite.add(self.world)
                if col == "P":
                    self.robo = Robo(x,y)
                    self.all_sprite.add(self.robo)
                x += 25
            y += 25
            x = 0

    def get_size(self):
        lines = self.level1
        line = max(lines, key=len)
        self.width = (len(line))*25
        self.height = (len(lines))*25
        return (self.width, self.height)

class Obstacle(pygame.sprite.Sprite):
    '''Class for creating  obstacles'''
    def __init__(self, x, y):
        self.x = x
        self.y = y
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Stage/wall.png").convert()
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

class GameRoom:

    def __init__(self, screen):

        self.Images = LoadImages()
        self.Sounds = LoadSounds()

        self.Sprites = pygame.sprite.RenderPlain()
        self.Ghost_sprites = pygame.sprite.RenderPlain()
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.screensize = screen.get_size()
        self.screen_rect = self.screen.get_rect()
        self.background = pygame.image.load("Stage/MoonLight.png").convert_alpha()
        self.background_rect = self.background.get_rect()
        level = Level("Level/levelTest")
        level.create_level(0,0)
        self.world = level.world
        self.robo = level.robo
        pygame.mouse.set_visible(0)
        self.font = pygame.font.Font(None, 60)
        self.GameOverFont = pygame.font.Font(None, 250)

        self.Images.load_strip('explosion.bmp', 71, 100, -1)
        self.Images.load_strip('ghost_right.png', 60, 60, -1)
        self.Images.load_strip('ghost_left.png', 60, 60, -1)
        self.Sounds.load_sound('explosion.wav')
        self.Projectiles = DepthUpdates()
        
        self.cheat = False
        self.dead = False
        self.spawnAmount = 25
        self.ghostCount = self.spawnAmount
        self.score = 0
        self.level = 1

        self.scoreText = self.font.render("Score: " + str(self.score), 1, (255,255,255))
        self.levelText = self.font.render("Level: " + str(self.level), 1, (255,255,255))
        self.gameOverText = self.GameOverFont.render("", 1, (255,255,255))

        for ghosts in range(0, self.spawnAmount):
            self.Ghost_sprites.add(Ghost(self.Images, self.screensize, self.Sprites, self.Sounds))
        self.Sprites.add(self.Ghost_sprites)

        self.camera = Camera(screen, self.robo.rect, level.get_size()[0], level.get_size()[1])
        self.all_sprite = level.all_sprite

    def run(self, events):

        # reload more enemies
        if self.ghostCount <= 5:
            self.spawnAmount += 10
            for ghosts in range(0, self.spawnAmount):
                self.Ghost_sprites.add(Ghost(self.Images, self.screensize, self.Sprites, self.Sounds))
            self.Sprites.add(self.Ghost_sprites)
            self.ghostCount = self.ghostCount + self.spawnAmount
            self.level += 1
            self.levelText = self.font.render("Level: " + str(self.level), 1, (255,255,255))

        
        # Handle collisions
        for ghost in self.Ghost_sprites:
            for otherGhost in pygame.sprite.spritecollide(ghost, self.Ghost_sprites, 0):
                if ghost != otherGhost:
                    bounce(ghost, otherGhost)
                for wall in pygame.sprite.spritecollide(ghost, self.world, 0):
                    bounce(ghost, wall)
                for shot in pygame.sprite.spritecollide(ghost, self.Projectiles, True):
                    shot.kill()
                    ghost.kill()
                    self.ghostCount -= 1
                    self.score += 1
                    self.scoreText = self.font.render("Score: " + str(self.score), 1, (255,255,255))
                if self.cheat == False:
                    if pygame.Rect.colliderect(ghost.rect, self.robo.rect):
                        self.dead = True

        if self.dead == True:
            self.robo.kill()
            self.gameOverText = self.GameOverFont.render("GAME OVER", 1, (255,255,255))
                    
        for shot in self.Projectiles:
            for wall in self.world:
               if pygame.Rect.colliderect(shot.rect, wall.rect):
                    shot.kill()

        up = left = right = shoot = False
        x, y = 0, 0

        pressed= pygame.key.get_pressed()
        if pressed[K_e]:
            right = True
        if pressed[K_w]:
            left = True
        if pressed[K_SPACE]:
            up = True
        if pressed[K_o]:
            shoot = True
        if pressed[K_j] and pressed[K_k] and pressed[K_l]:
            if self.cheat == False:
                self.cheat = True

        
        asize = ((self.screen_rect.w // self.background_rect.w + 1) * self.background_rect.w, (self.screen_rect.h // self.background_rect.h + 1) * self.background_rect.h)
        bg = pygame.Surface(asize)

        self.Sprites.update()

        for x in range(0, asize[0], self.background_rect.w):
            for y in range(0, asize[1], self.background_rect.h):
                self.screen.blit(self.background, (x, y))

        self.Sprites.draw(self.screen)
        self.camera.draw_sprites(self.screen, self.all_sprite)

        self.screen.blit(self.gameOverText, (350, 300))
        self.screen.blit(self.levelText, (100, 50))
        self.screen.blit(self.scoreText, (100, 100))
        self.robo.update(up, left, right, shoot, self.world)
        self.Projectiles.add(self.robo.getProjectiles())
        self.Sprites.add(self.robo.getProjectiles())
        self.Sprites.update()
        self.camera.update()
        pygame.display.flip()

