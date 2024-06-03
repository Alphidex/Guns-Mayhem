# Example file showing a basic pygame "game loop"
import pygame
import random
import math
# pygame setup
pygame.init()

# Display
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

background = pygame.image.load("game_background.png").convert_alpha()
background = pygame.transform.scale(background, screen.get_size())

def debug(info, y=10, x=10):
    font = pygame.font.Font()
    screen = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(screen, 'Black', debug_rect)
    screen.blit(debug_surf, debug_rect)

def timePassed(time):
    return pygame.time.get_ticks() - time

class Gun(pygame.sprite.Sprite):
    screen = pygame.display.get_surface()
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images.png").convert_alpha()
        self.image = self.image.subsurface((600, 0, 150, 150))
        self.rect = self.image.get_rect(topleft=pos)
        self.angle = 0

        # Starting position for bullets
        self.gunTipPos = [0, 0]


    def draw(self, flip):
        flippedImage = pygame.transform.flip(self.image, flip, False)
        screen.blit(flippedImage,  self.rect)

    def update(self, pos, flip):
        if pygame.mouse.get_focused():
            mousePos = pygame.mouse.get_pos()
            dx = mousePos[0] - pos[0]
            dy = mousePos[1] - pos[1]
            self.angle = math.degrees(math.atan2(-dy, dx))
        else:
            self.angle = 0

        offsetRad, offsetAngle = 30, math.radians(self.angle)
        offsetX, offsetY = offsetRad * math.cos(offsetAngle), -offsetRad * math.sin(offsetAngle)

        gunEndPointRad = 80
        self.gunTipPos = pygame.math.Vector2([gunEndPointRad * math.cos(offsetAngle + 0.2), -gunEndPointRad * math.sin(offsetAngle + 0.2)]) + self.rect.center

        self.rect.center = pos
        rotatedImage = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotatedImage.get_rect(center=self.rect.center + pygame.math.Vector2(offsetX,offsetY))
        screen.blit(rotatedImage, new_rect)

        # self.draw(flip)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, spawnPoint, screen, mousePos):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.pos = spawnPoint
        self.image = pygame.Surface((5, 5)).convert_alpha()


        self.speed = 12
        dy, dx = mousePos[1] - spawnPoint[1], mousePos[0] - spawnPoint[0]
        self.angle = math.degrees(math.atan2(dy, dx))
        self.dy, self.dx = self.speed * math.sin(math.radians(self.angle)), self.speed * math.cos(math.radians(self.angle))

    def draw(self):
        self.screen.blit(self.image, self.pos)

    def update(self):
        self.draw()
        self.pos += pygame.Vector2(self.dx, self.dy)

class BulletsGroup(pygame.sprite.Group):
    screen = pygame.display.get_surface()
    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def update(self, shoot, pos):
        mousePos = pygame.mouse.get_pos()
        if shoot:
            self.add(Bullet(pos, screen, mousePos))

        for sprite in self.sprites():
            sprite.update()
            if sprite.pos[0] > screen.get_width():
                sprite.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        guy = pygame.image.load("Tiny_Guy.png").convert_alpha()
        guy = pygame.transform.scale_by(guy, 0.5)
        guy_pos = [50, 100]

        self.image = guy
        self.rect = self.image.get_rect(topleft=guy_pos)
        self.screen = pygame.display.get_surface()

        self.flip = False

        self.vSpeed = 0
        self.jump = False
        self.jumpCount = 0
        self.dustParticles = 0
        self.shoot = False

        self.dash = False
        self.dashTime = 0
        self.afterImage = None

        self.gun = Gun(self.rect.center + pygame.math.Vector2(-12, 14))
        self.bullets = BulletsGroup()

    def draw(self):
        flippedImage = pygame.transform.flip(self.image, self.flip, False)
        self.screen.blit(flippedImage, self.rect)
    
    def update(self, events):
        GRAVITY = 1  # Acceleration

        key = pygame.key.get_pressed()

        dx = 0
        dy = 0
        
        if key[pygame.K_a]:
            dx -= 5
            self.flip = True
        elif key[pygame.K_d]:
            dx += 5
            self.flip = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.dash = True
                    self.dashTime = pygame.time.get_ticks()
                    self.afterImage = AfterImageEffect(pygame.transform.flip(self.image, self.flip, False))
                if event.key == pygame.K_w:
                    if self.jumpCount < 2:
                        self.jumpCount += 1
                        self.jump = True
                        self.vSpeed = -20
                        self.dustParticles = Dust(self.rect.midbottom)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.shoot = True

        if self.dash:
            if timePassed(self.dashTime) < 250:
                dx += 20 + (-40 * self.flip)
                self.afterImage.update(self.rect.topleft)
            else:
                self.dash = False

        if self.jump:
            self.dustParticles.update()

        dy += self.vSpeed

        if self.rect.bottom + dy < 500:
            self.vSpeed += GRAVITY
        else:
            dy = 500 - self.rect.bottom
            self.vSpeed = 0
            self.jump = False
            self.jumpCount = 0

        self.rect.x += dx
        self.rect.y += dy

        self.draw()
        self.gun.update((self.rect.center + pygame.math.Vector2(0, 14)), self.flip)

        self.bullets.update(self.shoot, list(self.gun.gunTipPos))
        self.shoot = False
    
player = Player()

class AfterImage(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.mask.from_surface(image).to_surface(setcolor=(104, 15, 95, 255), unsetcolor=None)
        self.pos = pos

    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def update(self, screen):
        self.draw(screen)

        # 0.4% chance that the radius will decrease by 1
        if random.randint(0, 100) < 40:
            self.image.set_alpha(self.image.get_alpha()-20)
        # If radius smaller than 0, then the sprite is killed
        if self.image.get_alpha() <= 0:
            self.kill()


class AfterImageEffect(pygame.sprite.Group):
    def __init__(self, image):
        pygame.sprite.Group.__init__(self)
        # self.add(AfterImage(pos, image))
        self.image = image
        self.screen = pygame.display.get_surface()

    def update(self, pos):
        if random.randint(1, 100) < 40:
            self.add(AfterImage(pos, self.image))

        # Updating the particles sprites and drawing them
        for particle in self.sprites():
            particle.update(self.screen)


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = pos[0], pos[1]  # Getting the initial postions of the player
        self.vx, self.vy = random.randint(-4, 4), random.randint(-10, 0) * .1 # Setting random movement speeds for the particles
        self.rad = 10 # The radius is 10 pixels

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.rad) # Drawing the particles

    def update(self):
        # Updating the speed of the particles
        self.x += self.vx
        self.y += self.vy
        # 0.4% chance that the radius will decrease by 1
        if random.randint(0, 100) < 40:
            self.rad -= 1
        # If radius smaller than 0, then the sprite is killed
        if self.rad <= 0:
            self.kill()


class Dust(pygame.sprite.Group):
    def __init__(self, pos):
        pygame.sprite.Group.__init__(self)
        self.pos = pos # Getting the player's position
        for i in range(50): # Creating 50 particles
            self.add(Particle(self.pos))
        self.screen = pygame.display.get_surface()

    def update(self):
        # Updating the particles sprites and drawing them
        for particle in self.sprites():
            particle.update()
        self.draw()

    def draw(self):
        for particle in self.sprites():
            particle.draw(self.screen)



while running:
    # fill the screen with a color to wipe away anything from last frame
    screen.blit(background, (0, 0))

    events = pygame.event.get()

    # Event loop
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Other code
    player.update(events)


    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

pygame.quit()