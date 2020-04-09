import os
import pickle
import pygame

#Importing objects from files
from Objects.plane import UserPlane
from Objects.rock import Rock
from Objects.base import Base

WIN_WIDTH = 500
WIN_HEIGHT = 800

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png")))

FIRE_IMGS = [pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire1.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire2.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire3.png")), (80, 80)),
             pygame.transform.scale(pygame.image.load(os.path.join("Images", "fire4.png")), (80, 80))]


pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
BUTTON_FONT = pygame.font.SysFont('Times New Roman', 15)


def draw_window(win, plane, rocks, base, score, high):
# def draw_window(win, plane, plane2, plane3, rocks, base, score, high):
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    # Draw the multiple rocks that should be on the screen using ROCK class draw method
    for rock in rocks:
        rock.draw(win)
    # Render the high score to the screen that is pulled from a file
    high_score = pygame.font.SysFont("comicsans", 50).render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (WIN_WIDTH - 10 - high_score.get_width(), 10))
    # Render the score to the screen
    score = pygame.font.SysFont("comicsans", 50).render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 45))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the plane
    plane.draw(win)
    #plane2.draw2(win)
    #plane3.draw2(win)
    #Updates the window with new visuals every frame
    pygame.display.update()


#def player_game(plane, plane2, plane3):
def player_game(plane):
    base = Base(670)
    rocks = [Rock(700)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    try:
        with open('./HighScoreFiles/highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0

    # Make the plane move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(30)
        # Moving and jumping of the plane
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                plane.jump()
                wait = False
        base.move()
        # draw_window(win, plane, plane2, plane3, rocks, base, 0, high)
        draw_window(win, plane, rocks, base, 0, high)

    # Keep track of how many rocks have been passed
    score = 0
    # will run until plane dies by the rock or the ground
    run = True
    fall = True
    while run:
        clock.tick(30)

        # Moving and jumping of the plane
        plane.move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                plane.jump()

        # Array to hold rocks that have left the screen and need to be removed
        rem = []
        # Only add passed rocks
        add_rock = False
        for rock in rocks:
            # If a plane pixels touches a rock pixel the plane will die
            if rock.collide(plane):
                run = False
            # If rock is completely off the screen
            if rock.x + rock.ROCK_TOP.get_width() < 0:
                rem.append(rock)
                # This will check if the plane has passed the rock
            if not rock.passed and rock.x < plane.x:
                rock.passed = True
                add_rock = True
            rock.move()
        # For all the rocks that have been passed we need to regenerate new ones
        if add_rock:
            # Signifies in the scoreboard that a rock has been passed
            score += 1
            if score > high:
                high += 1
            rocks.append(Rock(600))

        for r in rem:
            rocks.remove(r)

        # If the plane hits the ground
        if plane.y + plane.img.get_height() >= 780 or plane.y + plane.img.get_height() < -50:
            run = False

        if not run:
            while fall:
                clock.tick(40)
                if plane.y + plane.img.get_height() >= 780:
                    fall = False
                elif plane.y + plane.img.get_height() < 780:
                    plane.move()
                    i = 0
                    win.blit(FIRE_IMGS[i], (plane.x, plane.y))
                    i += 1
                    if i == 4:
                        i = 0
                    pygame.display.update()
                    #draw_window(win, plane, plane2, plane3, rocks, base, score, high)
                    draw_window(win, plane, rocks, base, score, high)

        base.move()
        #draw_window(win, plane, plane2, plane3, rocks, base, score, high)
        draw_window(win, plane, rocks, base, score, high)
    # Save the highest score of the session to file for later
    with open('./HighScoreFiles/highscores.dat', 'wb') as file:
        pickle.dump(high, file)


# Option button 1, regular game for the user to play
def option_one(win):
    plane = UserPlane(200, 350)
    # plane2 = UserPlane(30, 30)
    # plane3 = UserPlane(50, 70)
    # player_game(plane, plane2, plane3)
    player_game(plane)

    restart_game = pygame.Rect(180, 265, 134, 45)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), restart_game)
    # Give the button some text
    restart = pygame.font.SysFont('Times New Roman', 18).render("Restart Game", 1, (255, 255, 255))
    win.blit(restart, (200, 275))

    back_to_menu = pygame.Rect(180, 345, 134, 45)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), back_to_menu)
    # Give the button some text
    back = pygame.font.SysFont('Times New Roman', 18).render("Back To Menu", 1, (255, 255, 255))
    win.blit(back, (195, 355))
    pygame.display.update()

    clock = pygame.time.Clock()
    i = 0
    wait = True
    while wait:
        # Make the fire gif animation
        clock.tick(30)
        win.blit(FIRE_IMGS[i], (plane.x, plane.y))
        i += 1
        if i == 4:
            i = 0
        # Updates the window with new visuals every frame
        pygame.display.update()

        # Moving and jumping of the plane
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:

                if restart_game.collidepoint(event.pos):
                    # Whenever just the player is playing
                    option_one(win)
                    wait = False
                elif back_to_menu.collidepoint(event.pos):
                    # Whenever you want to watch the AI learn
                    wait = False
                    break
