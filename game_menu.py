import pygame
import neat
import time
import os
import pygame.freetype

# Importing objects from files
from Objects.plane import Plane
from Objects.base import Base

# Import the Game Options Functions
from GameOptions.user_playing import option_one
from GameOptions.AI_learning import option_two
from GameOptions.AI_trained import option_three

pygame.font.init()

# Got my images from this source
# https://github.com/odedw/elm-plane


def menu_window(win, plane, plane2, plane3, plane4, base, start_button1, start_button2, start_button3):
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png"))), (0, 0))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the plane
    plane.draw_spin(win)
    # Calls the helper function to actually draw the plane
    plane2.draw_spin(win)
    # Calls the helper function to actually draw the plane
    plane3.draw_spin(win)
    # Calls the helper function to actually draw the plane
    plane4.draw_spin(win)
    # Add Title Image to Game
    win.blit(pygame.transform.scale(pygame.image.load(os.path.join("Images", "title.png")), (300, 150)), (100, 105))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button1)
    # Give the button some text
    start1 = pygame.font.SysFont('Times New Roman', 15).render("Play Game", 1, (255, 255, 255))
    win.blit(start1, (217, 290))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button2)
    # Give the button some text
    start2 = pygame.font.SysFont('Times New Roman', 15).render("Watch AI Play", 1, (255, 255, 255))
    win.blit(start2, (205, 390))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button3)
    # Give the button some text
    start3 = pygame.font.SysFont('Times New Roman', 15).render("Watch Trained AI", 1, (255, 255, 255))
    win.blit(start3, (197, 490))
    # Updates the window with new visuals every frame
    pygame.display.update()


def main():
    plane = Plane(220, 570)
    plane2 = Plane(220, 50)
    plane3 = Plane(380, 330)
    plane4 = Plane(60, 290)
    plane.spin_count = 0
    plane2.spin_count = 21
    plane3.spin_count = 10
    plane4.spin_count = 31

    base = Base(690)

    win = pygame.display.set_mode((500, 800))
    clock = pygame.time.Clock()

    start_button1 = pygame.Rect(192, 285, 117, 30)
    start_button2 = pygame.Rect(192, 385, 117, 30)
    start_button3 = pygame.Rect(192, 485, 117, 30)

    # Make the bird move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(15)
        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if start_button1.collidepoint(event.pos):
                        # Whenever just the player is playing
                        option_one(win)
                    elif start_button2.collidepoint(event.pos):
                        # Whenever you want to watch the AI learn
                        option_two(win)
                    elif start_button3.collidepoint(event.pos):
                        # Whenever you want to watch a near perfect version of the AI
                        option_three(win)

        base.move()
        menu_window(win, plane, plane2, plane3, plane4, base, start_button1, start_button2, start_button3)

    pygame.quit()
    quit()


main()
