from typing import Any
import pygame
from pygame.locals import *
import random 

pygame.init()
clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Define color
white = (255, 255, 255)

# Game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
Pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_Pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# Load images
bg = pygame.image.load('bg.png')
ground = pygame.image.load('ground.png')
button_img = pygame.image.load('restart.png')

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    global score
    Pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        global flying, game_over
        # Gravity
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            # Jump
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Animation
            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[self.index]

            # Rotate bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # Bird falls down when game over
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        # Position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(Pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(Pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

bird_group = pygame.sprite.Group()
Pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:
    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    Pipe_group.draw(screen)
    screen.blit(ground, (ground_scroll, 768))

    # Check the score
    if len(Pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > Pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < Pipe_group.sprites()[0].rect.right \
                and not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > Pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # Check for collision
    if pygame.sprite.groupcollide(bird_group, Pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    # Check if bird hit the ground
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_Pipe > pipe_frequency:
            Pipe_height = random.randint(-100, 100)
            btm_Pipe = Pipe(screen_width, int(screen_height / 2) + Pipe_height, -1)
            top_Pipe = Pipe(screen_width, int(screen_height / 2) + Pipe_height, 1)
            Pipe_group.add(btm_Pipe)
            Pipe_group.add(top_Pipe)
            last_Pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        Pipe_group.update()

    # Check for game over and reset
    if game_over:
        if button.draw():
            game_over = False
            score = reset_game()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    pygame.display.update()

pygame.quit()
