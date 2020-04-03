import pygame
import os

# Loading the Ground to serve as a showing of plane moving
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "ground.png")))


# The floor of the game screen
class Base:
    # How fast the floor is moving, will be same as velocity of the rocks
    VEL = 5
    # The base will need to be rotated so we need to know its width
    WIDTH = BASE_IMG.get_width()
    # This is the literal image of the base being stored for later use
    IMG = BASE_IMG

    # x is changing so cant be defined
    def __init__(self, y):
        self.y = y
        # Making sure we have boundaries tracked to know when it needs to be reset
        self.x1 = 0
        self.x2 = self.WIDTH

    # called every single frame as the screen moves
    def move(self):
        # Both the left x and the right x boundary need to be seen as moving so they can be
        # Tracked. The importance of this comes into play later
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # Pretty much we will have two base images in the game at once.
        # This occurs when the first image leaves to the left of the screen, we will cycle it to the back
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        # This occurs when the second image leaves to the left of the screen, we will cycle it to the back
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
        # Above is a repeated cycling so that there is always a base at the bottom of the screen

    def draw(self, win):
        # Drawing the two rock images side by side to achieve rolling look
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
