import sys
import pygame
import time
import random
import math
import numpy as np

RES = [1200, 800]
WHITE = (255,255,255)
FRAME = [1100, 700]
BUILDING_IMAGE = pygame.image.load('images/building.png')
SALESMAN_IMAGE = pygame.image.load('images/salesman.png')
SALESMAN_NUM = 10
BUILDING_NUM = 47
SALESMAN_SIZE = (40, 40)
BUILDING_SIZE = (24, 24)
SALESMAN_RANGE = list(range(0, SALESMAN_NUM - 1))
BUILDING_RANGE = list(range(0, BUILDING_NUM - 1))

pygame.init()
FPS = 100
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode(RES)
SCREEN.fill(WHITE)

class Salesman():
    def __init__(self):
        self.locations = generate_init_salesman_locations(SALESMAN_NUM)
        self.image = pygame.transform.scale(SALESMAN_IMAGE, SALESMAN_SIZE)

    def draw(self):
        for location in self.locations:
            SCREEN.blit(self.image, (location[0], location[1]))

    def move(self):
        for i in range(SALESMAN_NUM):
            self.locations[i][0] += 10

class Building():
    def __init__(self):
        self.locations = generate_init_building_locations(BUILDING_NUM)
        self.image = pygame.transform.scale(BUILDING_IMAGE, BUILDING_SIZE)

    def draw(self):
        for location in self.locations:
            SCREEN.blit(self.image, (location[0], location[1]))

def generate_init_salesman_locations(num_salesman):
    locations = np.zeros((num_salesman, 2))
    for i in range(num_salesman):
        locations[i] = 100
    return locations

def generate_init_salesman_locations(num_salesman):
    locations = np.zeros((num_salesman, 2))
    for i in range(num_salesman):
        locations[i] = 100
    return locations

def generate_init_building_locations(num_buildings):
    locations = np.zeros((num_buildings, 2), dtype=np.int16)
    for i in range(num_buildings):
        locations[i][0] = random.choice(range(FRAME[0]))
        locations[i][1] = random.choice(range(FRAME[1]))
    return locations

if __name__ == "__main__":
    time.sleep(5)
    SALESMAN = Salesman()
    BUILDING = Building()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        SCREEN.fill(WHITE)
        SALESMAN.draw()
        BUILDING.draw()
        SALESMAN.move()
        pygame.display.flip()
        CLOCK.tick(FPS)
