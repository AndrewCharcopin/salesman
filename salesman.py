import sys
import pygame
import time
import random
import math
import pandas as pd
import csv
import numpy as np

RES = [1200, 800]
FRAME = [1100, 700]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CAPTION_POINT = (20, 20)
pygame.init()
font = pygame.font.Font(None, 18)
SCREEN = pygame.display.set_mode(RES)
pygame.display.set_caption("salesman")
SCREEN.fill(WHITE)

BUILDING_IMAGE = pygame.image.load('images/building.png')
HOME_IMAGE = pygame.image.load('images/home.png')
SALESMAN_IMAGE = pygame.image.load('images/salesman.png')
SALESMAN_SIZE = (40, 40)
BUILDING_SIZE = (20, 20)
HOME_SIZE = (30, 30)
START_POINT = (100, 100)

SALESMAN_NUM = 160 #must be mutilple of 4
BUILDING_NUM = 12
ELITE_NUM = int(SALESMAN_NUM/2)
P_MUTATION = 0.005
GENERATION = 1000

class Salesman():
    def __init__(self):
        self.locations = self.generate_init_salesman_locations()
        self.genes = self.generate_init_genes()
        self.image = pygame.transform.scale(SALESMAN_IMAGE, SALESMAN_SIZE)
        self.levels = np.zeros(SALESMAN_NUM, dtype=np.int16)
        self.total_distances = np.zeros(SALESMAN_NUM)
        self.speed = 100
        self.generation = 0
        self.history_total_distance = [0] * GENERATION
        self.history_shortest = [0] * GENERATION

    def draw(self):
        generation_text = font.render("generation: " + str(self.generation), True, BLACK)
        total_distances_text = font.render("total_distances: " + str(sum(self.total_distances)), True, BLACK)
        shortest_text = font.render("shortest: " + str(min(self.total_distances)), True, BLACK)
        SCREEN.blit(generation_text, (CAPTION_POINT[0], CAPTION_POINT[1] + 0))
        SCREEN.blit(total_distances_text, (CAPTION_POINT[0], CAPTION_POINT[1] + 20))
        SCREEN.blit(shortest_text, (CAPTION_POINT[0], CAPTION_POINT[1] + 40))
        for location in self.locations:
            SCREEN.blit(self.image, (location[0], location[1]))

    def move(self):
        for i in range(SALESMAN_NUM):
            if self.levels[i] == 0:
                start_place = START_POINT
                target_place = BUILDING.locations[self.genes[i][0]]
            elif 0 < self.levels[i] < BUILDING_NUM:
                start_place = BUILDING.locations[self.genes[i][self.levels[i]-1]]
                target_place = BUILDING.locations[self.genes[i][self.levels[i]]]
            elif self.levels[i] == BUILDING_NUM:
                start_place = BUILDING.locations[self.genes[i][self.levels[i]-1]]
                target_place = START_POINT
            if self.check_arrived(i) and self.levels[i] < BUILDING_NUM + 1:
                self.total_distances[i] += calculate_distance(start_place, target_place)
                self.history_total_distance[self.generation] = sum(self.total_distances)
                self.history_shortest[self.generation] = min(self.total_distances)
                self.levels[i] += 1
            if self.levels[i] < BUILDING_NUM + 1:
                angle = calculate_angle(start_place, target_place)
                dx = math.cos(math.radians(angle)) * self.speed
                dy = math.sin(math.radians(angle)) * self.speed
                distance = calculate_distance(self.locations[i], target_place)
                if distance <= math.sqrt(dx**2 + dy**2):
                    self.locations[i] = target_place
                else:
                    self.locations[i][0] += dx
                    self.locations[i][1] += dy

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

    def selection(self):
        chosen = self.roulette_choice()
        random.shuffle(chosen)
        it = iter(chosen)
        crossed_genes = np.zeros((SALESMAN_NUM - ELITE_NUM, BUILDING_NUM + 1), dtype=np.int16)
        for i, (a, b) in enumerate(zip(it, it)):
            child1, child2 = self.partial_crossover(self.genes[a], self.genes[b])
            crossed_genes[i*2] = child1
            crossed_genes[i*2+1] = child2
        mutated_genes = [self.translocation_mutation(crossed_gene) for crossed_gene in crossed_genes]
        elite_genes = self.generate_elite()
        new_genes = mutated_genes + elite_genes
        self.locations = self.generate_init_salesman_locations()
        self.levels = np.zeros(SALESMAN_NUM, dtype=np.int16)
        self.total_distances = np.zeros(SALESMAN_NUM)
        self.genes = [np.asarray(new_gene) for new_gene in new_genes]
        self.generation += 1

    def generate_elite(self):
        sorted_total_distances = sorted(self.total_distances)
        elite_genes = np.zeros((ELITE_NUM, BUILDING_NUM + 1), dtype=np.int16)
        for i, v in enumerate(sorted_total_distances[:ELITE_NUM]):
            find_index = np.where(self.total_distances == v)[0][0]
            elite_genes[i] = self.genes[find_index]
        return elite_genes.tolist()

    def generate_roulette(self):
        total = np.sum(self.total_distances)
        roulette = np.zeros(len(self.total_distances))
        for i in range(len(self.total_distances)):
            roulette[i] = 1-(self.total_distances[i]/total)
        roulette/=roulette.sum()
        return roulette

    def roulette_choice(self):
        roulette = self.generate_roulette()
        chosen = np.random.choice(len(roulette), int(SALESMAN_NUM/2), replace=True, p=roulette)
        return chosen

    def partial_crossover(self, parent1, parent2):
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

    def translocation_mutation(self, gene):
        mutated_gene = gene
        mutation_flg = np.random.choice(2, 1, p = [1-P_MUTATION, P_MUTATION])
        if mutation_flg == 1:
            mutation_value = np.random.choice(mutated_gene[:-1], 2, replace = False)
            mutation_position1 = np.where(gene == mutation_value[0])
            mutation_position2 = np.where(gene == mutation_value[1])
            mutated_gene[mutation_position1] = mutation_value[1]
            mutated_gene[mutation_position2] = mutation_value[0]
        return mutated_gene

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

def export_to_csv(SALESMAN):
    df_gene = pd.DataFrame(SALESMAN.genes)
    df_total_distance = pd.DataFrame(SALESMAN.history_total_distance, columns=['total'])
    df_shortest = pd.DataFrame(SALESMAN.history_shortest, columns=['shortest'])
    df_gene.to_csv("gene.csv")
    df_total_distance.to_csv("total_distance.csv")
    df_shortest.to_csv("shortest.csv")

if __name__ == "__main__":
    SALESMAN = Salesman()
    BUILDING = Building()
    while True:
        SCREEN.fill(WHITE)
        SALESMAN.move()
        if sum(SALESMAN.levels) == (BUILDING_NUM+1)*SALESMAN_NUM:
            SALESMAN.selection()
        if SALESMAN.generation == GENERATION:
            export_to_csv(SALESMAN)
            pygame.quit()
            sys.exit()
        SALESMAN.draw()
        BUILDING.draw()
        pygame.display.flip()
