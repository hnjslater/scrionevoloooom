import pygame, sys, math, random, os
from pygame.locals import *
import random
from constants import *
import constants
from random import randint


def load_image(name):
    image = pygame.image.load(name)
    image = image.convert_alpha()
    colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class SomeSprites(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
    def draw(self,win):
        pygame.sprite.Group.draw(self, win)
        for thing in self:
            thing.draw(win)
        
class HealthyThing(pygame.sprite.Sprite):
    def __init__(self,health):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.original_health = health
    def hurt(self,value):
        self.health -= value;
        if self.health <= 0:
            self.kill()
    def draw(self, win):
        if not self.health == self.original_health:
            x = self.rect.centerx +(self.rect.width/5)
            y = self.rect.centery+(self.rect.height/5)
            w = self.rect.width/2
            h = 10
            pygame.draw.rect(win, (0,0,0), (x,y,w,h), 0) 
            win.fill((0,255,0), (x,y,w*(float(self.health)/self.original_health),h)) 
            pygame.draw.rect(win, (255,255,255), (x,y,w,h), 1) 

class Goodie(HealthyThing):
    def __init__(self,x,y,ttheta,img):
        HealthyThing.__init__(self, 20)
        self.image, self.rect = load_image(img)
        self.ttheta = ttheta
        self.set_theta(0)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.dx = 0

    def set_theta(self,theta):
        self.tx = -math.sin(theta + self.ttheta)*50
        self.ty = -math.cos(theta + self.ttheta)*50

    def set_origin(self,x,y):
        self.rect.center = (x + self.tx, y + self.ty)

    def get_theta(self,theta):
        return ((theta + self.ttheta + math.pi) % (2 * math.pi)) - math.pi

class BulletShip(Goodie):
    def __init__(self,x,y,ttheta):
        Goodie.__init__(self,x,y,ttheta,'ship-bullet.png')
    def fire_bullets(self):
        return Bullet(self.rect.left + (self.rect.width/2), self.rect.top)

class ShieldShip(Goodie):
    def __init__(self,x,y,ttheta):
        Goodie.__init__(self,x,y,ttheta,'ship-shield.png')
    def fire_bullets(self):
        if len(constants.shields) < 2:
            return Shield(self.rect.left + (self.rect.width/2), self.rect.top - 50)
        else:
            return []

class CannonShip(Goodie):
    def __init__(self,x,y,ttheta):
        Goodie.__init__(self,x,y,ttheta,'ship-cannon.png')
        self.since_firing = 0
    def fire_bullets(self):
        if self.since_firing == 0:
            self.since_firing = 20
            return Missile(self.rect.left + (self.rect.width/2), self.rect.top)
        else:
            return []
    def update(self, *args):
        if self.since_firing > 0:
            self.since_firing = self.since_firing - 1



class HeartShip(HealthyThing):
    def __init__(self,x,y):
        HealthyThing.__init__(self,20)
        self.image, self.rect = load_image('ship-heart.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.set_origin(x,y)
    def set_origin(self,x,y):
        self.rect.center  = (x,y)
    def get_theta(self,theta):
        return 100
    def set_theta(self,theta):
        pass
    def kill(self):
        constants.PLAYING = False
        pygame.sprite.Sprite.kill(self)


class Goodies(SomeSprites):
    def __init__(self,x,y):
        pygame.sprite.Group.__init__(self)
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.dtheta = 0
        self.theta = 0
        first_goodie = BulletShip(x, y, 0)
        self.gunner = first_goodie
        self.add(first_goodie)
        self.add(ShieldShip(x, y, math.pi * 2/3))
        self.add(CannonShip(x, y, math.pi * 4/3))
        self.add(HeartShip(x, y));
        
    def start_moving_left(self):
            self.dx = -8;

    def stop_moving_left(self):
        if self.dx == -8:
            self.dx = 0;

    def start_moving_right(self):
        self.dx = 8;

    def stop_moving_right(self):
        if self.dx == 8:
            self.dx = 0;

    def start_rotating_left(self):
        self.dtheta = math.pi / 32

    def start_rotating_right(self):
        self.dtheta = -(math.pi / 32)

    def stop_rotating_left(self):
        if self.dtheta == math.pi / 32: 
            self.dtheta = 0

    def stop_rotating_right(self):
        if self.dtheta == -(math.pi / 32): 
            self.dtheta = 0

    def update(self, *arg):
        if self.dtheta != 0:
            self.theta = self.theta + self.dtheta
            for goodie in self:
                goodie.set_theta(self.theta)
                theta = goodie.get_theta(self.theta)
                if theta > -(math.pi/3) and theta < (math.pi/3):
                    self.gunner = goodie
                
        new_x = self.x + self.dx
        if new_x > 0 and new_x < SCREEN_SIZE:
            self.x = new_x

        for goodie in self:
            goodie.set_origin(self.x, self.y) 
            goodie.update(self, arg)

    def fire_bullets(self):
        if self.gunner in self:
            return self.gunner.fire_bullets()
        else:
            return []

            

class Baddie(HealthyThing):
    def __init__(self,x,y):
        HealthyThing.__init__(self, 4)
        self.image, self.rect = load_image('baddie.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.dx = 0
    def update(self, *arg):
        self.rect.top = self.rect.top + 5
        if self.rect.top > SCREEN_SIZE:
            self.kill()
    def bang(self, goodie):
        goodie.hurt(1)
        self.hurt(1)

class BigBaddie(HealthyThing):
    def __init__(self,x,y):
        HealthyThing.__init__(self, 300)
        self.image, self.rect = load_image('big-baddie.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.dx = 0
        constants.bigbaddies.add(self)
    def update(self, *arg):
        self.rect.top = self.rect.top + 1
        if self.rect.top > SCREEN_SIZE:
            self.kill()
    def bang(self, goodie):
        goodie.hurt(10)
        self.hurt(1)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('bullet.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = x - self.rect.width/2, y
    def update(self, *arg):
        self.rect.top = self.rect.top - 30
        if self.rect.top < 0:
            self.kill()
    def bang(self,baddie):
        self.kill()
        baddie.hurt(1)

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('bullet.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = x - self.rect.width/2, y
    def update(self, *arg):
        self.rect.top = self.rect.top - 5
        if self.rect.top < 0:
            self.kill()
    def bang(self,baddie):
        self.kill()
        baddie.hurt(100)

class Shield(HealthyThing):
    def __init__(self, x, y):
        HealthyThing.__init__(self,20)
        self.image, self.rect = load_image('shield.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = x - self.rect.width/2, y
        self.age = 0
        constants.shields.add(self)
    def update(self, *arg):
        self.age = self.age + 1
        if self.age > 60:
            self.kill()
    def bang(self,baddie):
        baddie.hurt(2)
        self.hurt(2)

class Welcome(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('intro.png')
        self.rect.center = (x, y)

class YouWin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('you-win.png')
        self.rect.center = (SCREEN_SIZE/2, 0)
    def update(self, *arg):
        self.rect.top = self.rect.top + 5
        if (self.rect.bottom > SCREEN_SIZE):
            constants.PLAYING = False
            self.rect.bottom = 0

def main():
	pygame.init()

        #pygame.mixer.music.load('backing_music.ogg')
        #pygame.mixer.music.play(-1, 0.0)

	fpsClock = pygame.time.Clock()

	win = pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))
	pygame.display.set_caption('game')

	welcome = pygame.sprite.Group(Welcome(SCREEN_SIZE/2, SCREEN_SIZE/2))
	you_win = pygame.sprite.Group(YouWin())
	frame_count = 0

	while True:
            win.fill(pygame.Color(0,0,0))
            if constants.PLAYING and frame_count > 2000:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                you_win.draw(win)
                you_win.update()
            elif constants.PLAYING:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                        
                    elif event.type == KEYDOWN:
                        if event.key == K_h:
                            constants.goodies.start_moving_left()
                        if event.key == K_l:
                            constants.goodies.start_moving_right()
                        if event.key == K_j:
                            constants.goodies.start_rotating_left()
                        if event.key == K_k:
                            constants.goodies.start_rotating_right()

                        if event.key == K_SPACE:
                            constants.bullets.add(constants.goodies.fire_bullets())
                            constants.goodies.stop_rotating_left()
                            constants.goodies.stop_rotating_right()

                    elif event.type == KEYUP:
                        if event.key == K_h:
                            constants.goodies.stop_moving_left()
                        if event.key == K_l:
                            constants.goodies.stop_moving_right()
                        if event.key == K_j:
                            constants.goodies.stop_rotating_left()
                        if event.key == K_k:
                            constants.goodies.stop_rotating_right()

                constants.goodies.update(win)
                constants.goodies.draw(win)

                constants.bullets.update(win)
                constants.bullets.draw(win)

                constants.baddies.update(win)
                constants.baddies.draw(win)

                collisions = pygame.sprite.groupcollide(constants.baddies, constants.bullets, False, False)
                for baddie in collisions:
                    some_bullets = collisions[baddie]
                    for bullet in some_bullets:
                        bullet.bang(baddie)
                    
                collisions = pygame.sprite.groupcollide(constants.goodies, constants.baddies, False, False)
                for goodie in collisions:
                    some_baddies = collisions[goodie]
                    for baddie in some_baddies:
                        baddie.bang(goodie)

                if len(constants.baddies) < (frame_count / 150) + 5:
                    if frame_count > 300 and randint(0,10) == 5 and len(constants.bigbaddies) < 3:
                        constants.baddies.add(BigBaddie(randint(0,SCREEN_SIZE),40))
                    else:
                        constants.baddies.add(Baddie(randint(0,SCREEN_SIZE),20))

                frame_count = frame_count + 1

            else:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYUP and event.key == K_SPACE:
                        constants.PLAYING = True
                        constants.goodies = Goodies(SCREEN_SIZE/2, 700)
                        constants.bullets = pygame.sprite.Group()
                        constants.baddies = SomeSprites()
                        constants.shields = pygame.sprite.Group()
                        constants.bigbaddies = pygame.sprite.Group()
                        frame_count = 0
                welcome.draw(win)


            pygame.display.update()
            fpsClock.tick(60)



main()
