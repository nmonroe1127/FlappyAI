import pygame
import os
import random


class Rock:
    # Height of rock is random so not passed in
    def __init__(self, coordinate_pos):
        # Current Coordinate position of the rock
        self.coordinate_pos = coordinate_pos
        # Length of the Rock to be placed
        self.length = random.randrange(100, 400)
        # Image if rock is attached to top of the screen, needs to be flipped
        self.ceiling_rock = pygame.transform.flip(
            pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bottomRock.png"))), False, True)
        # Image if the rock is attached to bottom of screen
        self.ground_rock = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bottomRock.png")))

        # Drawing the rock at a negative location so that there is room for plane to go through
        self.upper_bound = self.length - self.ceiling_rock.get_height()
        # Where the bottom of the rock will be drawn on the screen
        self.lower_bound = self.length + 200

        # If the rock has already passed the rock
        self.finished = False

    # Literally just moving it in x direction
    def move_left(self):
        self.coordinate_pos -= 5

    def draw(self, win):
        x_coordinate = self.coordinate_pos
        ceiling_y_coordinate = self.upper_bound
        ground_y_coordinate = self.lower_bound
        win.blit(self.ceiling_rock, (x_coordinate, ceiling_y_coordinate))
        win.blit(self.ground_rock, (x_coordinate, ground_y_coordinate))

    # Registering if the plane pixels collides with any of the rock pixels
    def collision_occurence(self, plane):
        # Finds the first point of collision between bottom rock and offset distance
        # IF there is no overlap, it will return "NONE", otherwise it shows collision
        if plane.get_mask().overlap(pygame.mask.from_surface(self.ground_rock), (self.coordinate_pos - plane.x, self.lower_bound - round(plane.y))):
            return True
        # Finds the first point of collision between top rock and offset distance
        elif plane.get_mask().overlap(pygame.mask.from_surface(self.ceiling_rock), (self.coordinate_pos - plane.x, self.upper_bound - round(plane.y))):
            return True
        # No collision has occurred
        else:
            return False
