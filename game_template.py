import math
import os
from pathlib import Path
import random
import sys
import neat
import pygame
from pygame.time import Clock


pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

ASSETS_DIR = Path(__file__).parent.resolve() / "Assets"

RUNNING = [pygame.image.load(ASSETS_DIR / "Dino" / "DinoRun1.png"),
           pygame.image.load(ASSETS_DIR / "Dino" / "DinoRun2.png")]

JUMPING = [pygame.image.load(ASSETS_DIR / "Dino" / "DinoJump.png")]

SMALL_CACTUS = [pygame.image.load(ASSETS_DIR / "Cactus" / "SmallCactus1.png"),
                pygame.image.load(ASSETS_DIR / "Cactus" / "SmallCactus2.png"),
                pygame.image.load(ASSETS_DIR / "Cactus" / "SmallCactus3.png")]
LARGE_CACTUS = [pygame.image.load(ASSETS_DIR / "Cactus" / "LargeCactus1.png"),
                pygame.image.load(ASSETS_DIR / "Cactus" / "LargeCactus2.png"),
                pygame.image.load(ASSETS_DIR / "Cactus" / "LargeCactus3.png")]

BG = pygame.image.load(ASSETS_DIR / "Other" / "Track.png")

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Dinosaur:

    JUMP_VEL = 8.5
    X_POS = 80
    Y_POS = 310

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dino_jump = False
        self.dino_run = True
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(
            self.X_POS,
            self.Y_POS,
            img.get_width(),
            img.get_height()
        )
        self.color = (random.randint(0, 255) for _ in range(3))
        self.step_index = 0 # Ranges from 0 to 9

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 0:
            self.step_index = 0

    def jump(self):
        self.image = JUMPING[0]
        if self.dino_jump:
            # Minus because higher altitude is lower y-value
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1
        

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))



class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        self.rect.y = 300


def remove(index):
    dinosaurs.pop(index)


def main():
    # Note from Renoir: Their tutorial uses global,
    # I did not choose to use it
    global game_speed, obstacles, dinosaurs, x_pos_bg, y_pos_bg, points
    clock = Clock()
    points = 0
    dinosaurs = [Dinosaur()]
    obstacles = []
    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 20

    def score():
        global points, game_speed
        points += 1
        if points % 100:
            game_speed += 1
        text = FONT.render(f"Points: {str(points)}", True, (0, 0, 0))
        SCREEN.blit(text, (950, 50))
    
    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        SCREEN.fill((255, 255, 255))
        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)
        if len(dinosaurs) == 0:
            break
        if len(obstacles) == 0:
            if random.randint(0, 1):
                obstacles.append(
                    SmallCactus(SMALL_CACTUS, random.randint(0, 2))
                )
            else:
                obstacles.append(
                    LargeCactus(LARGE_CACTUS, random.randint(0, 2))
                )
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for index, dinosaur in enumerate(dinosaurs):
                if dinosaur.rect.colliderect(obstacle.rect):
                    remove(index)
        user_input = pygame.key.get_pressed()
        for index, dinosaur in enumerate(dinosaurs):
            if user_input[pygame.K_SPACE]:
                dinosaur.dino_jump = True
                dinosaur.dino_run = False
        score()
        background()
        clock.tick(30)
        pygame.display.update()


def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return abs(complex(dx, dy))


def eval_genomes(genomes, config):
    # Note from Renoir: Their tutorial uses global,
    # I did not choose to use it
    global game_speed, obstacles, dinosaurs, x_pos_bg, y_pos_bg, points
    clock = Clock()
    points = 0
    ge = []
    nets = []
    dinosaurs = [Dinosaur()]
    obstacles = []
    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 20

    def score():
        global points, game_speed
        points += 1
        if points % 100:
            game_speed += 1
        text = FONT.render(f"Points: {str(points)}", True, (0, 0, 0))
        SCREEN.blit(text, (950, 50))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.bit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.bit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        SCREEN.fill((255, 255, 255))
        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)
        if len(dinosaurs) == 0:
            break
        if len(obstacles) == 0:
            if random.randint(0, 1):
                obstacles.append(
                    SmallCactus(SMALL_CACTUS, random.randint(0, 2))
                )
            else:
                obstacles.append(
                    LargeCactus(LARGE_CACTUS, random.randint(0, 2))
                )
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for index, dinosaur in enumerate(dinosaurs):
                ge[index].fitness -= 1
                if dinosaur.rect.colliderect(obstacle.rect):
                    remove(index)
        user_input = pygame.key.get_pressed()
        for index, dinosaur in enumerate(dinosaurs):
            output = nets[index].activate(
                (dinosaur.rect.y, distance((dinosaur.rect.x, dinosaur.rect.y)))
            )
        score()
        background()
        clock.tick(30)
        pygame.display.update()


if __name__ == "__main__":
    main()
