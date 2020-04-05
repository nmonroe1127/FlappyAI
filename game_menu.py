import pygame
import os
import pygame.freetype

# Importing objects from files
from Objects.plane import UserPlane
from Objects.base import Base

# Import the Game Options Functions
from GameOptions.user_playing import option_one
from GameOptions.AI_learning import option_two
from GameOptions.AI_trained import option_three
from GameOptions.user_against_AI import option_four

pygame.font.init()

# Got my images from this source
# https://github.com/odedw/elm-plane


def menu_window(win, plane, plane2, plane3, plane4, base, start_button1, start_button2, start_button3, start_button4):
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
    start1 = pygame.font.SysFont('Times New Roman', 18).render("Play Game", 1, (255, 255, 255))
    win.blit(start1, (210, 275))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button2)
    # Give the button some text
    start2 = pygame.font.SysFont('Times New Roman', 18).render("Watch AI Play", 1, (255, 255, 255))
    win.blit(start2, (195, 355))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button3)
    # Give the button some text
    start3 = pygame.font.SysFont('Times New Roman', 18).render("Watch Trained AI", 1, (255, 255, 255))
    win.blit(start3, (183, 435))
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), start_button4)
    # Give the button some text
    start3 = pygame.font.SysFont('Times New Roman', 18).render("Play Against AI", 1, (255, 255, 255))
    win.blit(start3, (190, 515))
    # Updates the window with new visuals every frame
    pygame.display.update()


def main():
    plane = UserPlane(220, 570)
    plane2 = UserPlane(220, 50)
    plane3 = UserPlane(380, 330)
    plane4 = UserPlane(60, 290)
    plane.spin_count = 0
    plane2.spin_count = 21
    plane3.spin_count = 10
    plane4.spin_count = 31

    base = Base(690)

    win = pygame.display.set_mode((500, 800))
    clock = pygame.time.Clock()

    start_button1 = pygame.Rect(180, 265, 134, 45)
    start_button2 = pygame.Rect(180, 345, 134, 45)
    start_button3 = pygame.Rect(180, 425, 134, 45)
    start_button4 = pygame.Rect(180, 505, 134, 45)

    # Make the plane move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(15)
        # Moving and jumping of the plane
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
                    elif start_button4.collidepoint(event.pos):
                        option_four(win)

        base.move()
        menu_window(win, plane, plane2, plane3, plane4, base, start_button1, start_button2, start_button3, start_button4)

    pygame.quit()
    quit()


main()
