import sys
import pygame
import time
import random
import math
import numpy as np

RES = [1200, 800]
FRAME = [1100, 700]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CAPTION_POINT = (20, 20)
FPS = 200
pygame.init()
CLOCK = pygame.time.Clock()
font = pygame.font.Font(None, 18)
SCREEN = pygame.display.set_mode(RES)
pygame.display.set_caption("salesman")
SCREEN.fill(WHITE)

BUILDING_IMAGE = pygame.image.load('images/building.png')
HOME_IMAGE = pygame.image.load('images/home.png')
SALESMAN_IMAGE = pygame.image.load('images/salesman.png')
SALESMAN_NUM = 20
BUILDING_NUM = 3
SALESMAN_SIZE = (40, 40)
BUILDING_SIZE = (20, 20)
HOME_SIZE = (30, 30)
START_POINT = (100, 100)

ELITE = int(SALESMAN_NUM * 0.2)
P_MUTATION = 0.005

class Salesman():
    def __init__(self):
        self.locations = self.generate_init_salesman_locations()
        self.genes = self.generate_init_genes()
        self.image = pygame.transform.scale(SALESMAN_IMAGE, SALESMAN_SIZE)
        self.levels = np.zeros(SALESMAN_NUM, dtype=np.int16)
        self.total_distances = np.zeros(SALESMAN_NUM)
        self.speed = 6.0
        self.generation = 0
        self.history_total_distances = [0]
        self.history_shortest = [0]

    def draw(self):
        total_distances_text = font.render("total_distances: " + str(sum(self.total_distances)), True, BLACK)
        shortest_text = font.render("shortest: " + str(min(self.total_distances)), True, BLACK)
        generation_text = font.render("generation: " + str(self.generation), True, BLACK)
        SCREEN.blit(total_distances_text, CAPTION_POINT)
        SCREEN.blit(shortest_text, (CAPTION_POINT[0], CAPTION_POINT[1] + 20))
        SCREEN.blit(generation_text, (CAPTION_POINT[0], CAPTION_POINT[1] + 40))
        for location in self.locations:
            SCREEN.blit(self.image, (location[0], location[1]))

    def move(self):
        for i in range(SALESMAN_NUM):
            if self.check_arrived(i) and self.levels[i] < BUILDING_NUM + 1:
                self.levels[i] += 1
            if self.levels[i] == BUILDING_NUM:
                angle = calculate_angle(self.locations[i], START_POINT)
            elif self.levels[i] <= BUILDING_NUM:
                target_place = BUILDING.locations[self.genes[i][self.levels[i]]]
                angle = calculate_angle(self.locations[i], target_place)
            if self.levels[i] < BUILDING_NUM + 1:
                target_place = BUILDING.locations[self.genes[i][self.levels[i]]]
                dx = math.cos(angle) * self.speed
                dy = math.sin(angle) * self.speed
                distance = calculate_distance(self.locations[i], target_place)
                if distance <= 3.3*(dx**2 + dy**2):
                    self.locations[i] = target_place
                else:
                    self.locations[i][0] += dx
                    self.locations[i][1] += dy
                self.total_distances[i] += calculate_distance([(self.locations[i][0] - dx), (self.locations[i][1] - dy)], self.locations[i])

    def check_arrived(self, i):
        if self.levels[i] > BUILDING_NUM:
            return True
        else:
            target_place = BUILDING.locations[self.genes[i][self.levels[i]]]
            distance = calculate_distance(self.locations[i], target_place)
        if distance == 0:
            return True
        else:
            return False

    def selection(self):
        chosen = roulette_choice(self.total_distances)
        random.shuffle(chosen)
        it = iter(chosen)
        crossed_genes = np.zeros((int(SALESMAN_NUM/2), BUILDING_NUM + 1), dtype=np.int16)
        for i, (a, b) in enumerate(zip(it, it)):
            child1, child2 = partial_crossover(self.genes[a], self.genes[b])
            crossed_genes[i*2] = child1
            crossed_genes[i*2+1] = child2
        mutated_genes = [translocation_mutation(crossed_gene) for crossed_gene in crossed_genes]
        next_generation = self.generation + 1
        history_shortest = self.history_shortest.append(min(self.total_distances))
        history_total_distances = self.history_shortest.append(sum(self.total_distances))
        elite = [self.genes[i] for i in chosen]
        new_genes = mutated_genes + elite
        self.__init__()
        self.genes = [np.asarray(new_gene) for new_gene in new_genes]
        self.generation = next_generation
        self.history_total_distances = history_total_distances
        self.history_shortest = history_shortest

    def generate_init_genes(self):
        genes = np.zeros((SALESMAN_NUM, BUILDING_NUM + 1), dtype=np.int16)
        for i in range(SALESMAN_NUM):
            random_gene = random.sample(range(BUILDING_NUM), BUILDING_NUM)
            random_gene.append(BUILDING_NUM)
            genes[i] = random_gene
        return genes

    def generate_init_salesman_locations(self):
        locations = np.zeros((SALESMAN_NUM, 2))
        for i in range(SALESMAN_NUM):
            locations[i] = START_POINT[0]
        return locations

class Building():
    def __init__(self):
        self.locations = self.generate_init_building_locations()
        self.image = pygame.transform.scale(BUILDING_IMAGE, BUILDING_SIZE)
        self.home_image = pygame.transform.scale(HOME_IMAGE, HOME_SIZE)

    def draw(self):
        SCREEN.blit(self.home_image, (self.locations[-1][0], self.locations[-1][1]))
        for i in range(BUILDING_NUM):
            SCREEN.blit(self.image, (self.locations[i][0], self.locations[i][1]))

    def generate_init_building_locations(self):
        locations = np.zeros((BUILDING_NUM + 1, 2), dtype=np.int16)
        for i in range(BUILDING_NUM):
            locations[i][0] = random.choice(range(FRAME[0]))
            locations[i][1] = random.choice(range(FRAME[1]))
        locations[-1] = START_POINT
        return locations

def calculate_distance(a, b):
    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

def calculate_angle(a, b):
    radian = math.atan2(b[1] - a[1], b[0] - a[0])
    return math.degrees(radian)

def generate_roulette(total_distances):
    total = np.sum(total_distances)
    roulette = np.zeros(len(total_distances))
    for i in range(len(total_distances)):
        roulette[i] = 1/(total_distances[i]*total)
    roulette/=roulette.sum()
    return roulette

def roulette_choice(total_distances):
    roulette = generate_roulette(total_distances)
    chosen = np.random.choice(len(roulette), int(SALESMAN_NUM/2), replace=True, p=roulette)
    return chosen

def partial_crossover(parent1, parent2):
    num = len(parent1)
    cross_point = random.randrange(1, num-1)
    child1 = parent1
    child2 = parent2
    for i in range(num - cross_point):
        target_index = cross_point + i
        target_value1 = parent1[target_index]
        target_value2 = parent2[target_index]
        exchange_index1 = np.where(parent1 == target_value2)
        exchange_index2 = np.where(parent2 == target_value1)
        child1[target_index] = target_value2
        child2[target_index] = target_value1
        child1[exchange_index1] = target_value1
        child2[exchange_index2] = target_value2
    return child1.tolist(), child2.tolist()

def translocation_mutation(gene):
    mutated_gene = gene
    mutation_flg = np.random.choice(2, 1, p = [1-P_MUTATION, P_MUTATION])
    if mutation_flg == 1:
        print("muted")
        mutation_value = np.random.choice(mutated_gene[:-1], 2, replace = False)
        mutation_position1 = np.where(gene == mutation_value[0])
        mutation_position2 = np.where(gene == mutation_value[1])
        mutated_gene[mutation_position1] = mutation_value[1]
        mutated_gene[mutation_position2] = mutation_value[0]
    return mutated_gene

if __name__ == "__main__":
    SALESMAN = Salesman()
    BUILDING = Building()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        SCREEN.fill(WHITE)
        SALESMAN.move()
        if sum(SALESMAN.levels) == (BUILDING_NUM+1)*SALESMAN_NUM:
            SALESMAN.selection()
        SALESMAN.draw()
        BUILDING.draw()
        pygame.display.flip()
        CLOCK.tick(FPS)
