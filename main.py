import pygame, sys, math, random, os
from pygame.locals import *
import random
from constants import *
import constants
from random import randint


#functions to create our resources
def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class Goodie(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('Brewdog-Logo-blue.png', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 700
        self.dx = 0


    def start_moving_left(self):
        self.dx = 8;

    def stop_moving_left(self):
        if self.dx == 8:
            self.dx = 0;

    def start_moving_right(self):
        self.dx = -8;

    def stop_moving_right(self):
        if self.dx == -8:
            self.dx = 0;

    def fire_bullets(self):
        return (Bullet(self.rect.left, self.rect.top), Bullet(self.rect.right, self.rect.top))
        

    def update(self, *arg):
        new_left = self.rect.left + self.dx
        if new_left > 0 and new_left + self.rect.width < SCREEN_SIZE:
            self.rect.left = new_left


class Baddie(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('Stella-Artois-chalice.png', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = x, y
        self.dx = 0
    def update(self, *arg):
        self.rect.top = self.rect.top + 10
        if self.rect.top > SCREEN_SIZE:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('Brewdog-Logo-blue-small.png', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = x, y
    def update(self, *arg):
        self.rect.top = self.rect.top - 30
        if self.rect.top < 0:
            self.kill()



def main():
	pygame.init()

        #pygame.mixer.music.load('backing_music.ogg')
        #pygame.mixer.music.play(-1, 0.0)

	fpsClock = pygame.time.Clock()

	win = pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))
	pygame.display.set_caption('game')
	font = pygame.font.Font(None, 20)

        goodies = []
        goodies.append(Goodie())
        
        allsprites = pygame.sprite.RenderPlain(goodies)
        bullets = pygame.sprite.RenderPlain()
        baddies = pygame.sprite.RenderPlain()
        baddies.add(Baddie(10,10))
        baddies.add(Baddie(50,10))
        baddies.add(Baddie(400,10))
	while True:
            win.fill(pygame.Color(0,0,0))


            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == KEYDOWN:
                    if event.key == K_l:
                            goodies[0].start_moving_left()
                    if event.key == K_h:
                            goodies[0].start_moving_right()
                    if event.key == K_SPACE:
                            bullets.add(goodies[0].fire_bullets())
                elif event.type == KEYUP:
                    if event.key == K_l:
                            goodies[0].stop_moving_left()
                    if event.key == K_h:
                            goodies[0].stop_moving_right()




            allsprites.update(win)
            allsprites.draw(win)

            bullets.update(win)
            bullets.draw(win)

            baddies.update(win)
            baddies.draw(win)

            pygame.sprite.groupcollide(bullets, baddies, True, True)

            if len(baddies) < 3:
                baddies.add(Baddie(randint(0,SCREEN_SIZE),20))

            pygame.display.update()
            fpsClock.tick(60)



main()
