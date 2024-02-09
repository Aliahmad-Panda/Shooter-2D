import pygame
from sys import exit
from pygame.sprite import Group
import random
import math 

pygame.init()

fps = 60

screen_width = 800
screen_height = 400

bg_surface = pygame.image.load("graphics/background/background_02.png")
bg_surface = pygame.transform.scale(bg_surface, (screen_width, screen_height))
bg_rect = bg_surface.get_rect(midbottom = (screen_width/2, screen_height))
scroll = 0
tiles = math.ceil(screen_width /bg_surface.get_width()) + 1

def draw_health_bar(screen, x, y, health_pct):
    # Set the dimensions and color of the health bar
    bar_width = 75
    bar_height = 7
    border_color = (255, 255, 255)  # white
    health_color = (255, 0, 0)  # red

    # Calculate the width of the health bar based on the health percentage
    health_width = int(bar_width * health_pct)

    # Draw the border of the health bar
    pygame.draw.rect(screen, border_color, (x, y, bar_width, bar_height))
    # Draw the health bar
    pygame.draw.rect(screen, health_color, (x, y, health_width, bar_height))

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Metal Slug")

bullets_player = pygame.sprite.Group()
bullets_npcs = pygame.sprite.Group()
npcs = pygame.sprite.Group()

class Solider(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.player_walk = [pygame.image.load('graphics/player/player_walk_right_1.png').convert_alpha(), pygame.image.load('graphics/player/player_walk_right_2.png').convert_alpha()]
        # player_walk_left = [pygame.image.load('graphics/player/player_walk_left_1.png').convert_alpha(), pygame.image.load('graphics/player/player_walk_left_2.png').convert_alpha()]
        # self.player_walk = [player_walk_right,player_walk_left]
        self.player_jump = pygame.image.load('graphics/player/jump_right.png')
        # player_jump_left = pygame.image.load('graphics/player/jump_left.png')
        # self.player_jump = [player_jump_right, player_jump_left]
        self.player_index = 0
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (x,y))
        self.gravity = 0
        self.in_air = False
        self.alive = True
        self.shoot_cooldown = 0
        self.move_right = False
        self.move_left = False
        self.sitting = False
        self.x = x
        self.y = y
        self.speed = 3
        self.facing_left = False
        self.shoot = False
        self.health = 1000
        self.weapon = Weapon(self.rect.midright, 0)
    
    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and not self.in_air:
            self.gravity = -20
            self.in_air = True    
        elif keys[pygame.K_s]: self.sitting = True
        if keys[pygame.K_d]:
            self.move_right = True
            self.facing_left = False
            self.weapon.facing_left = False
        elif keys[pygame.K_a]:
            self.move_left = True
            self.facing_left = True
            self.weapon.facing_left = True
        if keys[pygame.K_SPACE]:
                self.weapon.shoot() 
                
    def move(self):
        if self.move_right:
            if not self.in_air:
                if self.player_index + 0.1 < len(self.player_walk):
                    self.player_index += 0.15
                else: self.player_index = 0
            if self.rect.right <= 800:
                self.rect.right += self.speed 
                self.weapon.rect.right += self.speed
            else:
                global scroll
                global npcs
                scroll -= self.speed
                for npc in npcs:
                    npc.rect.x -= self.speed
                    npc.init -= self.speed
            self.move_right = False
        elif self.move_left:
            if not self.in_air:
                if self.player_index + 0.1< len(self.player_walk):
                    self.player_index += 0.15 
                else: self.player_index = 0
            if self.rect.left >= 0:
                self.rect.left -= self.speed
                self.weapon.rect.left -= self.speed
            else:
                scroll += self.speed 
                for npc in npcs:
                    npc.rect.x += self.speed
                    npc.init += self.speed
            self.move_left = False
        self.rect.bottom += self.gravity
        self.weapon.rect.bottom += self.gravity
        if self.rect.bottom>=400:
            self.rect.bottom = 400
            self.gravity = 0
            self.in_air = False
            self.weapon.rect.center = self.rect.midright
        self.gravity += 2

    def Shoot(self):
        if self.shoot:
            bullets_player.add(Bullet(self.rect.midleft if  self.facing_left else self.rect.midright , not self.facing_left))
            self.shoot = False
        if self.shoot_cooldown>0:
            self.shoot_cooldown-=1

    def get_hit(self):
        collisions = pygame.sprite.spritecollide(self, bullets_npcs, True)
        self.health -= int(len(collisions)) * 10        

    def death(self):
        if self.health <= 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        if not self.facing_left:
            self.weapon.rect.center = self.rect.midright
            screen.blit(self.weapon.image, self.weapon.rect.topleft)
        else:
            self.weapon.rect.center = self.rect.midleft
            screen.blit(pygame.transform.flip(self.weapon.image, True, False), self.weapon.rect.topleft)

    def update(self):
        self.player_input()
        self.weapon.update()
        self.move()
        if self.in_air:
            if self.facing_left:
                self.image = pygame.transform.flip(self.player_jump, True, False)
            else:
                self.image = self.player_jump
        else:
            if self.facing_left:
                self.image = pygame.transform.flip(self.player_walk[int(self.player_index)], True, False)
            else:
                self.image = self.player_walk[int(self.player_index)]
        # self.weapon.shoot()
        self.get_hit()
        self.death()
       
class World(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, xy, is_right):
        super().__init__()
        self.image = pygame.image.load('graphics/bullet/bullet.png')
        self.image = pygame.transform.scale(self.image, (30, 10))
        self.rect = self.image.get_rect(midright = xy)
        self.is_right = is_right

    def move(self):
        if self.is_right:
            self.rect.right += 8
        else:
            self.rect.left -= 8
        if self.rect.left >= 850 or self.rect.right <=-50:
            self.kill()

    def update(self):
        self.move()
        
class Weapon(pygame.sprite.Sprite):
    def __init__(self, xy, type):
        super().__init__()
        self.image = pygame.image.load(f'graphics/guns/gun_{type}.png')
        self.image = pygame.transform.scale(self.image, (70, 30))
        self.rect = self.image.get_rect(center = xy)
        self.shoot_cooldown = 0      
        self.type = type  
        self.facing_left = False

    def shoot(self):
        if not self.shoot_cooldown:
            bullets_player.add(Bullet(self.rect.midright if not self.facing_left else self.rect.midleft, not self.facing_left))
            self.shoot_cooldown = 20 if self.type == 0 else 8
        if self.shoot_cooldown>0:
            self.shoot_cooldown-=1
            
class Decoration(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

class NPC(pygame.sprite.Sprite):
    def __init__(self, xy):
        super().__init__()
        npc_walk_right = [pygame.image.load('graphics/player/player_walk_right_1.png').convert_alpha(), pygame.image.load('graphics/player/player_walk_right_2.png').convert_alpha()]
        npc_walk_left = [pygame.image.load('graphics/player/player_walk_left_1.png').convert_alpha(), pygame.image.load('graphics/player/player_walk_left_2.png').convert_alpha()]
        self.npc_walk = [npc_walk_right,npc_walk_left]
        self.npc_index = 0
        self.image = self.npc_walk[0][self.npc_index]
        self.rect = self.image.get_rect(midbottom = xy)
        self.health = 100
        self.facing_left = True #if random.randint(0 ,1) else False
        self.shoot_cooldown = 0
        self.shoot = False #if random.randint(0 ,1) else True
        self.speed = 3
        self.init = self.rect.x
        self.gravity = 0
        # self.vision_area = pygame.Rect(self.rect.right - 150, self.rect.top, self.rect.right - self.rect.left + 150, self.rect.bottom - self.rect.top)

    def get_hit(self):
        collisions = pygame.sprite.spritecollide(self, bullets_player, True)
        self.health -= int(len(collisions)) * 10

    def death(self):
        if self.health <= 0:
            global score
            score += 1 
            self.kill()

    def vision(self):
        if self.facing_left:
            self.vision_area = pygame.Rect(self.rect.right - 200, self.rect.top, self.rect.right - self.rect.left + 200 , self.rect.bottom - self.rect.top)
        else: 
            self.vision_area = pygame.Rect(self.rect.left, self.rect.top, self.rect.right - self.rect.left + 200, self.rect.bottom - self.rect.top)
        for playe in player:
            if pygame.Rect.colliderect(playe.rect, self.vision_area):
                self.shoot = True
                return
        self.shoot = False
    
    def Shoot(self):
        if self.shoot and not self.shoot_cooldown:
            bullets_npcs.add(Bullet(self.rect.midright if not self.facing_left else self.rect.midleft, not self.facing_left))
            self.shoot_cooldown = 40
            self.shoot = False
        if self.shoot_cooldown>0:
            self.shoot_cooldown-=1

    def move(self):
        if not self.shoot:
            if not self.facing_left:
                if self.npc_index + 0.1 < len(self.npc_walk):
                        self.npc_index += 0.15
                else: self.npc_index = 0
                # if self.rect.right < 800:
                #     self.rect.right += self.speed
                # else:
                #     self.facing_left = True 
                self.rect.right += self.speed
                self.move_right = False
                if self.rect.x - self.init>=150:
                    self.facing_left = True
            elif self.facing_left:
                if self.npc_index + 0.1< len(self.npc_walk):
                        self.npc_index += 0.15 
                else: self.npc_index = 0
                # if self.rect.left > 0:
                #     self.rect.left -= self.speed
                # else:
                #     self.facing_left = False
                self.rect.left -= self.speed
                if self.init - self.rect.x>=150:
                    self.facing_left = False 

    def side(self):
        if self.facing_left:
            self.image = self.npc_walk[1][int(self.npc_index)]
        else:
            self.image = self.npc_walk[0][int(self.npc_index)]

    def update(self):
        if self.rect.bottom < 400:
            self.rect.bottom += self.gravity
            self.gravity += 1
        else:
            self.rect.bottom = 400
            self.get_hit()
            self.death()      
            self.vision()  
            self.Shoot()
            self.move()
            self.side()


clock = pygame.time.Clock()
player = pygame.sprite.GroupSingle()
player.add(Solider(50, 385))
npcs.add(NPC((600 ,400)))

score = 0
font = pygame.font.Font("font/Pixeltype.ttf", 50)



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    for i in range(tiles):      
        if scroll<0:
            screen.blit(bg_surface, ((i*bg_surface.get_width() + scroll), 0))
        else:
            screen.blit(bg_surface, ((-i*bg_surface.get_width() + scroll), 0))
    if abs(scroll) >bg_surface.get_width():
        scroll = 0

    for npc in npcs:
        draw_health_bar(screen, npc.rect.x, npc.rect.y - 12, npc.health/100)

    for play in player:
        play.draw(screen)
        draw_health_bar(screen, play.rect.x, play.rect.y - 12, play.health/1000)
        
    player.update()
    bullets_player.draw(screen)
    bullets_player.update()
    bullets_npcs.draw(screen)
    bullets_npcs.update()
    npcs.draw(screen)
    npcs.update()
    if not len(npcs):
        npcs.add(NPC((random.randint(50, 750), 00))),
    score_sur = font.render(str(score), False, "red")
    if score>1:
        for players in player:
            players.weapon.type = 1
    screen.blit(score_sur, (400, 50))
    pygame.display.update()
    clock.tick(fps)