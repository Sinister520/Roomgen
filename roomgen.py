#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      conno
#
# Created:     10-11-2024
# Copyright:   (c) conno 2024
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions and fullscreen mode
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Set to fullscreen
WIDTH, HEIGHT = screen.get_size()  # Get fullscreen dimensions
pygame.display.set_caption("Planar Graph with Coulomb's Law and MST")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Physics settings
MIN_DISTANCE = 100  # Minimum distance between rectangles for Coulomb force
COULOMB_CONSTANT = 4000  # Moderate repulsive force
MAX_FORCE = 5  # Maximum force to limit repulsion effect
DAMPING_FACTOR = 0.95  # Damping to slow down movement

# Rectangle settings
MAX_RECTANGLES = 200
RECT_SIZE = (40, 20)

# Rectangle class
class Rectangle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width, self.height = RECT_SIZE
        self.vx = random.uniform(-0.5, 0.5)  # Small initial velocity
        self.vy = random.uniform(-0.5, 0.5)

    def apply_repulsion(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < MIN_DISTANCE and distance != 0:  # Apply repulsion if too close
            force = min(COULOMB_CONSTANT / (distance ** 2), MAX_FORCE)  # Limit force
            angle = math.atan2(dy, dx)

            # Repulsive force components
            fx = math.cos(angle) * force
            fy = math.sin(angle) * force

            # Update velocities based on repulsion
            self.vx -= fx
            self.vy -= fy
            other.vx += fx
            other.vy += fy

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Apply damping to gradually reduce speed
        self.vx *= DAMPING_FACTOR
        self.vy *= DAMPING_FACTOR
        # Keep within screen bounds
        if self.x < 0: self.x = 0
        if self.y < 0: self.y = 0
        if self.x + self.width > WIDTH: self.x = WIDTH - self.width
        if self.y + self.height > HEIGHT: self.y = HEIGHT - self.height

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))

    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

# Initialize rectangle list and spawn timer
rectangles = []
last_spawn_time = pygame.time.get_ticks()

# Helper function to calculate distance between two points
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Connect rectangles' centers using MST approach
def connect_rectangles_mst(surface, rectangles):
    centers = [rect.center() for rect in rectangles]
    edges = []

    # Create all edges between pairs of rectangles
    for i, center1 in enumerate(centers):
        for j, center2 in enumerate(centers):
            if i < j:
                edges.append((distance(center1, center2), i, j))

    # Sort edges by distance
    edges.sort()

    # Use union-find to avoid cycles and connect using MST
    parent = list(range(len(rectangles)))

    def find(x):
        while x != parent[x]:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rootX = find(x)
        rootY = find(y)
        if rootX != rootY:
            parent[rootY] = rootX
            return True
        return False

    # Draw edges that are part of the MST
    for edge in edges:
        dist, i, j = edge
        if union(i, j):
            pygame.draw.line(surface, BLACK, centers[i], centers[j], 1)

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False  # Exit the program if Escape is pressed

    # Check if it's time to spawn a new rectangle
    current_time = pygame.time.get_ticks()
    if len(rectangles) < MAX_RECTANGLES and current_time - last_spawn_time >= 100:
        # Spawn new rectangle in the center of the screen
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        new_rect = Rectangle(center_x, center_y)
        rectangles.append(new_rect)
        last_spawn_time = current_time

    # Apply Coulomb's repulsion between all rectangles
    for i, rect1 in enumerate(rectangles):
        for rect2 in rectangles[i+1:]:  # Avoid double calculations
            rect1.apply_repulsion(rect2)

    # Update and draw rectangles
    for rect in rectangles:
        rect.update()
        rect.draw(screen)

    # Connect rectangle centers with MST lines
    connect_rectangles_mst(screen, rectangles)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
