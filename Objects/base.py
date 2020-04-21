import pygame
import os

# The floor of the game screen
class Base:
    # x is changing so cant be defined
    def __init__(self, coordinate_pos):
        self.coordinate_pos = coordinate_pos
        # Making sure we have boundaries tracked to know when it needs to be reset
        self.leftmost_x = 0
        self.rightmost_x = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "ground.png"))).get_width()
        self.width = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "ground.png"))).get_width()

    def draw(self, win):
        # Drawing the two rock images side by side to achieve rolling look
        win.blit(pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "ground.png"))), (self.leftmost_x, self.coordinate_pos))
        win.blit(pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "ground.png"))), (self.rightmost_x, self.coordinate_pos))

    def replace_base(self):
        # Pretty much we will have two base images in the game at once.
        # This occurs when the first image leaves to the left of the screen, we will cycle it to the back
        if self.leftmost_x + self.width < 0:
            self.leftmost_x = self.rightmost_x + self.width
        # This occurs when the second image leaves to the left of the screen, we will cycle it to the back
        if self.rightmost_x + self.width < 0:
            self.rightmost_x = self.leftmost_x + self.width
        # Above is a repeated cycling so that there is always a base at the bottom of the screen

    # called every single frame as the screen moves
    def move(self):
        # Both the left x and the right x boundary need to be seen as moving so they can be
        # Tracked. The importance of this comes into play later
        self.leftmost_x -= 5
        self.rightmost_x -= 5
        # Check if base needs to be reset to continuously loop
        self.replace_base()
