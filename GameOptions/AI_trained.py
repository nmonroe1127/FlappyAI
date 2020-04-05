import pickle
import pygame
import os
import neat
import pygame.freetype

# Importing Objects from files
from neat.nn import FeedForwardNetwork

from Objects.plane import AIPlane
from Objects.rock import Rock
from Objects.base import Base

menu = True
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png")))

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
BUTTON_FONT = pygame.font.SysFont('Times New Roman', 15)

WIN_WIDTH = 500
WIN_HEIGHT = 800

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
gen = 0


def ai_window(win, planes, rocks, base, score, high, gen, full_size):
    # .blit() is basically just draw for pygame
    # Place the background image center on the screen or (0,0) due to Pygame orientation
    win.blit(BG_IMG, (0, 0))
    # Draw the multiple rocks that should be on the screen using ROCK class draw method
    for rock in rocks:
        rock.draw(win)
    # Render the high score to the screen that is pulled from a file
    high_score = STAT_FONT.render("High Score: " + str(high), 1, (0, 0, 0))
    win.blit(high_score, (WIN_WIDTH - 10 - high_score.get_width(), 10))
    # Render the score to the screen
    score = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 45))
    # Render the generation number to the screen
    score = STAT_FONT.render("Gen: " + str(gen), 1, (0, 0, 0))
    win.blit(score, (10, 10))
    # Render the number of plane left alive
    score_label = STAT_FONT.render("Alive: " + str(len(planes)) + "/" + str(full_size), 1, (0, 0, 0))
    win.blit(score_label, (10, 50))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the plane
    for plane in planes:
        plane.draw(win)

    stop = pygame.Rect(10, 85, 50, 30)
    pygame.draw.rect(win, (30, 30, 30), stop)
    back = pygame.font.SysFont('Times New Roman', 19).render("Stop", 1, (255, 255, 255))
    win.blit(back, (15, 90))
    global menu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if stop.collidepoint(event.pos):
                    menu = False
                    

    # Updates the window with new visuals every frame
    pygame.display.update()


# This will hold the code for watching the AI learn
def eval_genomes(genomes, config):
    """
        runs the simulation of the current population of
        planes and sets their fitness based on the distance they
        reach in the game.
        """
    global WIN, gen
    win = WIN
    gen += 1
    # print("Generation: " + str(gen))
    with open('./AIConfigurations/config-best.txt', 'rb') as f:
        c = pickle.load(f)
    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # plane object that uses that network to play
    nets = []
    planes = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        # net = FeedForwardNetwork.create(genome, config)
        net = FeedForwardNetwork.create(c, config)
        nets.append(net)
        planes.append(AIPlane(230, 350))
        ge.append(genome)

    full_size = len(planes)

    base = Base(690)
    rocks = [Rock(700)]
    score = 0

    clock = pygame.time.Clock()

    try:
        with open('./HighScoreFiles/AI_highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0


    run = True
    while run and len(planes) > 0:
        # clock.tick(30)
        if menu == False:
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        rock_ind = 0
        if len(planes) > 0:
            if len(rocks) > 1 and planes[0].x > rocks[0].x + rocks[0].ROCK_TOP.get_width():  # determine whether to use the first or second
               rock_ind = 1  # rock on the screen for neural network input

        for x, plane in enumerate(planes):  # give each plane a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            plane.move()

            # send plane location, top rock location and bottom rock location and determine from network whether to jump or not
            output = nets[planes.index(plane)].activate(
                (plane.y, abs(plane.y - rocks[rock_ind].height), abs(plane.y - rocks[rock_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                plane.jump()

        base.move()

        rem = []
        add_rock = False
        for rock in rocks:
            # check for collision
            for plane in planes:
                if rock.collide(plane):
                    ge[planes.index(plane)].fitness -= 1
                    nets.pop(planes.index(plane))
                    ge.pop(planes.index(plane))
                    planes.pop(planes.index(plane))

            if rock.x + rock.ROCK_TOP.get_width() < 0:
                rem.append(rock)

            if not rock.passed and rock.x < plane.x:
                rock.passed = True
                add_rock = True
            rock.move()
        if add_rock:
            score += 1
            # can add this line to give more reward for passing through a rock (not required)
            for genome in ge:
                genome.fitness += 5
            rocks.append(Rock(600))

        for r in rem:
            rocks.remove(r)

        for plane in planes:
            if plane.y + plane.img.get_height() - 10 >= 690 or plane.y < -50:
                nets.pop(planes.index(plane))
                ge.pop(planes.index(plane))
                planes.pop(planes.index(plane))
 
        ai_window(win, planes, rocks, base, score, high, gen, full_size)

        # break if score gets large enough
        #if score == 100:
            # ge[0].fitness = 1000000
            #break
       
    # print(score)
    # Save the highest score of the session to file for later
    if high < score:
        with open('./HighScoreFiles/AI_highscores.dat', 'wb') as file:
            pickle.dump(score, file)


def run(config_path, generations):
    # # Defining all of the subheadings found in the config text file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Generate a population
    p = neat.Population(config)
    # load the winner
    p.run(eval_genomes, 1)
    # This will run for however many generations we choose. This case is 50
    # winner = p.run(eval_genomes, generations)
    # with open('./AIConfigurations/config-best.txt', 'wb') as file:
    #     pickle.dump(winner, file)


def configuration(generations):
    # Finding the file that will hold the neural network and GA configurations
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AIConfigurations")
    config_path = os.path.join(local_dir, "config-single.txt")
    # Run the file that contains the neural network configurations
    run(config_path, generations)


# Option button 1, regular game for the user to play
def option_three(win):
    global menu
    menu = True
    # Give user the ability to choose the number of generations and population size
    configuration(20)

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
    # Updates the window with new visuals every frame
    pygame.display.update()

    wait = True
    while wait:

        # Moving and jumping of the plane
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if restart_game.collidepoint(event.pos):
                        # Whenever just the player is playing
                        option_three(win)
                    elif back_to_menu.collidepoint(event.pos):
                        # Whenever you want to watch the AI learn
                        wait = False
                        break

