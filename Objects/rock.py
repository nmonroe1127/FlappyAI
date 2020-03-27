import pygame
import os
import random

# Loading the Rocks to serve as obstacles
ROCK_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "bottomRock.png")))

class Rock:
    # Space between two rocks
    GAP = 200
    # Pipes move, not the plane
    VELOCITY = 5

    # Height of rock is random so not passed in
    def __init__(self, x):
        self.x = x
        self.height = 0

        # This is so that it can be attached to top or bottom of frame and tracked easily
        # Where the top of the rock will be drawn on the screen
        self.top = 0
        # Where the bottom of the rock will be drawn on the screen
        self.bottom = 0
        # Image if rock is attached to top of the screen, needs to be flipped
        self.ROCK_TOP = pygame.transform.flip(ROCK_IMG, False, True)
        # Image if the rock is attached to bottom of screen
        self.ROCK_BOTTOM = ROCK_IMG

        # If the rock has already passed the pipe
        self.passed = False
        # Will define top, bottom, and length of pipes
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        # Drawing the rock at a negative location so that there is room for plane to go through
        self.top = self.height - self.ROCK_TOP.get_height()
        self.bottom = self.height + self.GAP

    # Literally just moving it in x direction
    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.ROCK_TOP, (self.x, self.top))
        win.blit(self.ROCK_BOTTOM, (self.x, self.bottom))

    # Registering if the plane pixels collides with any of the rock pixels
    def collide(self, plane):
        # Get the pixels that define a plane
        plane_mask = plane.get_mask()
        # Get the pixels that define the top rock
        top_mask = pygame.mask.from_surface(self.ROCK_TOP)
        # Get the pixels that define the bottom rock
        bottom_mask = pygame.mask.from_surface(self.ROCK_BOTTOM)

        # Define an offset to find the distance between the plane pixels and top rock pixels
        top_offset = (self.x - plane.x, self.top - round(plane.y))
        # Define an offset to find the distance between the plane pixels and bottom rock pixels
        bottom_offset = (self.x - plane.x, self.bottom - round(plane.y))

        # Finds the first point of collision between bottom rock and offset distance
        # IF there is no overlap, it will return "NONE", otherwise it shows collision
        b_point = plane_mask.overlap(bottom_mask, bottom_offset)
        # Finds the first point of collision between top rock and offset distance
        t_point = plane_mask.overlap(top_mask, top_offset)

        # Check to see if either choice is not NONE
        if t_point or b_point:
            # This is if there is a collision
            return True
        # This is if there is no collision
        return False
