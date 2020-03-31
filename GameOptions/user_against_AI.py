import os
import pickle
import pygame
import neat
import pygame.freetype

#Importing objects from files
from Objects.plane import UserPlane
from Objects.rock import Rock
from Objects.base import Base
from Objects.plane import AIPlane
from neat.nn import FeedForwardNetwork

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

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
gen = 0


def ai_window(win, bird, plane, pipes, base, score, high):
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    # Draw the multiple pipes that should be on the screen using PIPE class draw method
    for pipe in pipes:
        pipe.draw(win)
    # Render the high score to the screen that is pulled from a file
    high_score = STAT_FONT.render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (WIN_WIDTH - 10 - high_score.get_width(), 10))
    # Render the score to the screen
    score = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 45))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the birdy
    bird.draw(win)
    plane.draw(win)
    # Updates the window with new visuals every frame
    pygame.display.update()


def draw_window(win, plane, bird, pipes, base, score, high):
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
    # Draw the AI
    bird.draw(win)
    # Calls the helper function to actually draw the birdy
    plane.draw(win)
    # Updates the window with new visuals every frame
    pygame.display.update()


# This will hold the code for watching the AI learn
def user_vs_AI(config, plane):
    base = Base(690)
    pipes = [Rock(700)]

    # Setup the AI plane
    with open('./AIConfigurations/config-best.txt', 'rb') as f:
        c = pickle.load(f)
    bird = AIPlane(200, 350)
    net = FeedForwardNetwork.create(c, config)

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
        draw_window(win, plane, bird, pipes, base, 0, high)

    # Keep track of how many pipes have been passed
    score = 0
    # will run until birdy dies by the pipe or the ground
    run = True
    fall = True
    while run:
        clock.tick(30)

        # Moving and jumping of the bird
        plane.move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                plane.jump()

        pipe_ind = 0
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].ROCK_TOP.get_width():  # determine whether to use the first or second
            pipe_ind = 1  # pipe on the screen for neural network input

        bird.move()

        # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
        output = net.activate(
            (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

        if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
            bird.jump()

        # Array to hold pipes that have left the screen and need to be removed
        rem = []
        # Only add passed pipes
        add_pipe = False
        for pipe in pipes:
            # If a bird pixels touches a pipe pixel the bird will die
            if pipe.collide(plane):
                run = False
            if pipe.collide(bird):
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

        if bird.y + bird.img.get_height() >= 730:
            run = False

        if run == False:
            while fall == True:
                clock.tick(40)
                if plane.y + plane.img.get_height() >= 730:
                    fall = False
                elif plane.y + plane.img.get_height() < 730:
                    plane.move()
                    i = 0
                    win.blit(FIRE_IMGS[i], (plane.x, plane.y))
                    i += 1
                    if i == 4:
                        i = 0
                    pygame.display.update()
                    draw_window(win, plane, bird, pipes, base, score, high)
                elif bird.y + bird.img.get_height() < 730:
                    bird.move()
                    i = 0
                    win.blit(FIRE_IMGS[i], (bird.x, bird.y))
                    i += 1
                    if i == 4:
                        i = 0
                    pygame.display.update()
                    draw_window(win, plane, bird, pipes, base, score, high)

        base.move()
        draw_window(win, plane, bird, pipes, base, score, high)

    # Save the highest score of the session to file for later
    with open('./HighScoreFiles/highscores.dat', 'wb') as file:
        pickle.dump(high, file)


def run(config_path, plane):
    # # Defining all of the subheadings found in the config text file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    user_vs_AI(config, plane)


def configuration(plane):
    # Finding the file that will hold the neural network and GA configurations
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AIConfigurations")
    config_path = os.path.join(local_dir, "config-single.txt")
    # Run the file that contains the neural network configurations
    run(config_path, plane)


# Option button 1, regular game for the user to play
def option_four(win):
    plane = UserPlane(200, 350)
    configuration(plane)

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
                        option_four(win)
                    elif back_to_menu.collidepoint(event.pos):
                        # Whenever you want to watch the AI learn
                        wait = False