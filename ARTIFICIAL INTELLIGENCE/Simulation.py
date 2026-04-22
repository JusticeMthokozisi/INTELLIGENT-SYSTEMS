# simulation.py
# This code has all core logic and classes of bees and it actions.

import pygame
import random
import math

class States:
    WANDERING = 'Wandering'
    FORAGING = 'Foraging'
    ATTACKING = 'Attacking'

class GridObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Bee(GridObject):
    def __init__(self, id, x, y):
        super().__init__(x, y)
        self.id = id
        self.health = 100
        self.energy = 100
        self.pollen = 0
        self.state = States.WANDERING

    def agent_function(self, flowers, threats, pheromone_grid, hive):
        
        # Check for death conditions first
        if self.health <= 0 or self.energy <= 0:
            return "die"

        # Percepts: Check the immediate surroundings
        nearby_flowers = self.find_nearby(flowers, 1)
        nearby_threats = self.find_nearby(threats, 1)
        has_pheromones = pheromone_grid[self.y][self.x] > 0
        at_hive = self.x == hive.x and self.y == hive.y

        # Finite State Machine transitions and actions
        if self.state == States.WANDERING:
            if nearby_threats or has_pheromones:
                self.state = States.ATTACKING
            elif nearby_flowers:
                self.state = States.FORAGING
            else:
                self.move_randomly()
                self.energy -= 1
        
        elif self.state == States.FORAGING:
            if self.pollen == 0:
                target = self.find_nearest(flowers)
                if target:
                    self.move_to(target)
                    self.energy -= 1
                    if self.x == target.x and self.y == target.y:
                        self.pollen = 1
                        self.energy = 100
                        flowers.remove(target)
                        self.state = States.WANDERING
            else:
                self.move_to(hive)
                self.energy -= 1
                if at_hive:
                    self.pollen = 0
                    self.health = 100
                    self.state = States.WANDERING
        
        elif self.state == States.ATTACKING:
            if not nearby_threats and not has_pheromones:
                self.state = States.WANDERING
            elif nearby_threats:
                target = random.choice(nearby_threats)
                self.move_to(target)
                self.energy -= 1
                if self.x == target.x and self.y == target.y:
                    threats.remove(target)
                    self.health -= 10
                    return "release_pheromones"
            else:
                self.move_randomly()
                self.energy -= 1
        
        return "continue"
    
    def move_randomly(self):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.move(dx, dy)

    def move_to(self, target):
        dx = 0
        dy = 0
        if self.x < target.x:
            dx = 1
        elif self.x > target.x:
            dx = -1
        if self.y < target.y:
            dy = 1
        elif self.y > target.y:
            dy = -1
        self.move(dx, dy)

    def move(self, dx, dy):
        new_x = max(0, min(Simulation.GRID_SIZE - 1, self.x + dx))
        new_y = max(0, min(Simulation.GRID_SIZE - 1, self.y + dy))
        self.x = new_x
        self.y = new_y

    def find_nearby(self, objects, distance):
        return [obj for obj in objects if math.sqrt((obj.x - self.x)**2 + (obj.y - self.y)**2) <= distance]

    def find_nearest(self, objects):
        if not objects:
            return None
        return min(objects, key=lambda obj: math.sqrt((obj.x - self.x)**2 + (obj.y - self.y)**2))

class Hive(GridObject):
    pass

class Flower(GridObject):
    pass

class Threat(GridObject):
    pass

class Simulation:
    # Colors
    LIGHT_BLUE = (207, 255, 254)
    DARK_BLUE = (59, 130, 246)
    YELLOW = (253, 224, 71)
    HIVE_YELLOW = (250, 204, 21)
    PINK = (190, 24, 93)
    RED = (239, 68, 68)

    # Constants
    GRID_SIZE = 50
    CELL_SIZE = 25
    NUM_BEES = 15
    NUM_FLOWERS = 30
    NUM_THREATS = 10

    def __init__(self):
        self.bees = []
        self.flowers = []
        self.threats = []
        self.hive = None
        self.pheromone_grid = []

        # Load and scale images with the updated file path
        self.bee_img = pygame.image.load('images/bee.png')
        self.bee_img = pygame.transform.scale(self.bee_img, (self.CELL_SIZE, self.CELL_SIZE))
        self.flower_img = pygame.image.load('images/flower.jpg')
        self.flower_img = pygame.transform.scale(self.flower_img, (self.CELL_SIZE, self.CELL_SIZE))
        self.threat_img = pygame.image.load('images/threat.png')
        self.threat_img = pygame.transform.scale(self.threat_img, (self.CELL_SIZE, self.CELL_SIZE))
        self.hive_img = pygame.image.load('images/beehive.jpg')
        self.hive_img = pygame.transform.scale(self.hive_img, (self.CELL_SIZE * 2, self.CELL_SIZE * 2))


    def setup(self):
        self.bees = []
        self.flowers = []
        self.threats = []
        self.pheromone_grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        
        self.hive = Hive(self.GRID_SIZE // 2, self.GRID_SIZE // 2)

        for i in range(self.NUM_BEES):
            self.bees.append(Bee(i, self.hive.x, self.hive.y))

        for _ in range(self.NUM_FLOWERS):
            self.flowers.append(Flower(random.randint(0, self.GRID_SIZE-1), random.randint(0, self.GRID_SIZE-1)))

        for _ in range(self.NUM_THREATS):
            self.threats.append(Threat(random.randint(0, self.GRID_SIZE-1), random.randint(0, self.GRID_SIZE-1)))

    def draw(self, screen):
        screen.fill(self.LIGHT_BLUE)

        # Draw pheromones
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                strength = self.pheromone_grid[y][x]
                if strength > 0:
                    alpha = int(255 * (strength / 10))
                    pheromone_color = (self.RED[0], self.RED[1], self.RED[2], alpha)
                    s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
                    s.fill(pheromone_color)
                    screen.blit(s, (x * self.CELL_SIZE, y * self.CELL_SIZE))

        # Draw grid lines
        for x in range(self.GRID_SIZE):
            for y in range(self.GRID_SIZE):
                rect = pygame.Rect(x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(screen, self.DARK_BLUE, rect, 1)

        # Draw Hive
        hive_rect = self.hive_img.get_rect(center=(self.hive.x * self.CELL_SIZE + self.CELL_SIZE // 2, self.hive.y * self.CELL_SIZE + self.CELL_SIZE // 2))
        screen.blit(self.hive_img, hive_rect)

        # Draw Flowers
        for flower in self.flowers:
            flower_rect = self.flower_img.get_rect(center=(flower.x * self.CELL_SIZE + self.CELL_SIZE // 2, flower.y * self.CELL_SIZE + self.CELL_SIZE // 2))
            screen.blit(self.flower_img, flower_rect)

        # Draw Threats
        for threat in self.threats:
            threat_rect = self.threat_img.get_rect(center=(threat.x * self.CELL_SIZE + self.CELL_SIZE // 2, threat.y * self.CELL_SIZE + self.CELL_SIZE // 2))
            screen.blit(self.threat_img, threat_rect)

        # Draw Bees
        for bee in self.bees:
            bee_rect = self.bee_img.get_rect(center=(bee.x * self.CELL_SIZE + self.CELL_SIZE // 2, bee.y * self.CELL_SIZE + self.CELL_SIZE // 2))
            screen.blit(self.bee_img, bee_rect)
            if bee.pollen > 0:
                pygame.draw.circle(screen, self.PINK, (bee.x * self.CELL_SIZE + self.CELL_SIZE // 2, bee.y * self.CELL_SIZE + self.CELL_SIZE // 2), self.CELL_SIZE // 8)

        pygame.display.flip()

    def update(self):
        # Update bees and filter out dead ones
        new_bees = []
        for bee in self.bees:
            result = bee.agent_function(self.flowers, self.threats, self.pheromone_grid, self.hive)
            if result == "die":
                continue
            if result == "release_pheromones":
                self.release_pheromones(bee)
            new_bees.append(bee)
        self.bees = new_bees
        
        # Decay pheromones
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                self.pheromone_grid[y][x] = max(0, self.pheromone_grid[y][x] - 1)

    def release_pheromones(self, bee):
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                dist = math.sqrt((x - bee.x)**2 + (y - bee.y)**2)
                if dist <= 10:
                    strength = max(0, 10 - int(dist))
                    self.pheromone_grid[y][x] = max(self.pheromone_grid[y][x], strength)