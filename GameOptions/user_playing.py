import os
import pickle
import pygame

#Importing objects from files
from Objects.plane import Plane
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


def draw_window(win, plane, pipes, base, score, high):
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    # Draw the multiple pipes that should be on the screen using PIPE class draw method
    for pipe in pipes:
        pipe.draw(win)
    # Render the high score to the screen that is pulled from a file
    high_score = pygame.font.SysFont("comicsans", 50).render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (WIN_WIDTH - 10 - high_score.get_width(), 10))
    # Render the score to the screen
    score = pygame.font.SysFont("comicsans", 50).render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 45))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the birdy
    plane.draw(win)
    # Updates the window with new visuals every frame
    pygame.display.update()


def player_game(plane):
    base = Base(690)
    pipes = [Rock(700)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    try:
        with open('./HighScoreFiles/highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0

    # Make the bird move as it waits for the user to start the game
    wait = True
    while wait:
        clock.tick(30)
        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                plane.jump()
                wait = False
        base.move()
        draw_window(win, plane, pipes, base, 0, high)

    # Keep track of how many pipes have been passed
    score = 0
    # will run until birdy dies by the pipe or the ground
    run = True
    while run:
        clock.tick(30)

        # Moving and jumping of the bird
        plane.move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                plane.jump()

        # Array to hold pipes that have left the screen and need to be removed
        rem = []
        # Only add passed pipes
        add_pipe = False
        for pipe in pipes:
            # If a bird pixels touches a pipe pixel the bird will die
            if pipe.collide(plane):
                run = False
            # If pipe is completely off the screen
            if pipe.x + pipe.ROCK_TOP.get_width() < 0:
                rem.append(pipe)
                # This will check if the bird has passed the pipe
            if not pipe.passed and pipe.x < plane.x:
                pipe.passed = True
                add_pipe = True
            pipe.move()
        # For all the pipes that have been passed we need to regenerate new ones
        if add_pipe:
            # Signifies in the scoreboard that a pipe has been passed
            score += 1
            if score > high:
                high += 1
            pipes.append(Rock(600))

        for r in rem:
            pipes.remove(r)

        # If the bird hits the ground
        if plane.y + plane.img.get_height() >= 730:
            run = False

        base.move()
        draw_window(win, plane, pipes, base, score, high)

    # Save the highest score of the session to file for later
    with open('./HighScoreFiles/highscores.dat', 'wb') as file:
        pickle.dump(high, file)


# Option button 1, regular game for the user to play
def option_one(win):
    plane = Plane(200, 350)
    player_game(plane)

    restart_game = pygame.Rect(192, 220, 117, 30)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), restart_game)
    # Give the button some text
    restart = BUTTON_FONT.render("Restart Game", 1, (255, 255, 255))
    win.blit(restart, (210, 225))

    back_to_menu = pygame.Rect(192, 320, 117, 30)
    # Draw da buttons
    pygame.draw.rect(win, (30, 30, 30), back_to_menu)
    # Give the button some text
    back = BUTTON_FONT.render("Back To Menu", 1, (255, 255, 255))
    win.blit(back, (205, 325))

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

        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if restart_game.collidepoint(event.pos):
                        # Whenever just the player is playing
                        option_one(win)
                    elif back_to_menu.collidepoint(event.pos):
                        # Whenever you want to watch the AI learn
                        wait = False
