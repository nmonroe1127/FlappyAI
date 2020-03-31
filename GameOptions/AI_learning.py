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

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png")))

pygame.font.init()

STAT_FONT = pygame.font.SysFont("comicsans", 50)
BUTTON_FONT = pygame.font.SysFont('Times New Roman', 15)

WIN_WIDTH = 500
WIN_HEIGHT = 800

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
gen = 0


def ai_window(win, birds, pipes, base, score, high, gen, full_size):
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
    # Render the generation number to the screen
    score = STAT_FONT.render("Gen: " + str(gen), 1, (0, 0, 0))
    win.blit(score, (10, 10))
    # Render the number of plane left alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)) + "/" + str(full_size), 1, (0, 0, 0))
    win.blit(score_label, (10, 50))
    # call the method that will draw the ground into the game
    base.draw(win)
    # Calls the helper function to actually draw the birdy
    for bird in birds:
        bird.draw(win)
    # Updates the window with new visuals every frame
    pygame.display.update()


# This will hold the code for watching the AI learn
def eval_genomes(self, genomes, config, generations):
    global WIN, gen
    win = WIN
    gen += 1
    print("Generation: " + str(gen))

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(AIPlane(230, 350))
        ge.append(genome)

    full_size = len(birds)

    base = Base(690)
    pipes = [Rock(700)]
    score = 0

    clock = pygame.time.Clock()

    try:
        with open('./HighScoreFiles/AI_highscores.dat', 'rb') as file:
            high = pickle.load(file)
    except:
        high = 0


    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].ROCK_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1  # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.ROCK_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5
            pipes.append(Rock(600))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= 690 or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        ai_window(win, birds, pipes, base, score, high, gen, full_size)

        # break if score gets large enough
        if score == 20:
            break
    # Save the highest score of the session to file for later
    if high < score:
        with open('./HighScoreFiles/AI_highscores.dat', 'wb') as file:
            pickle.dump(score, file)


def run(config_path, generations):
    # Defining all of the subheadings found in the config text file
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Generate a population
    p = neat.Population(config)

    # This will print to the terminal some progress of the program each generation
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # This will run for however many generations we choose. This case is 50
    winner = p.run(eval_genomes, generations)
    print('\nBest genome:\n{!s}'.format(winner))


def configuration(population_size, generations):
    # Finding the file that will hold the neural network and GA configurations
    local_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AIConfigurations")
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    # Opening the file so that we can write to it
    config_file = open(config_path, "w+")
    # Setting up values for the neural network
    config_file.write("[NEAT]\n")
    config_file.write("fitness_criterion     = max\n")
    config_file.write("fitness_threshold     = 100000\n")
    config_file.write("pop_size              = " + str(population_size) + "\n")
    config_file.write("reset_on_extinction   = False\n\n")

    # Setting up values for the Default Genome
    config_file.write("[DefaultGenome]\n")
    # Node activation is done first
    config_file.write("activation_default      = tanh\n")
    config_file.write("activation_mutate_rate  = 0.0\n")
    config_file.write("activation_options      = tanh\n")
    # Now Node Aggregation Options
    config_file.write("aggregation_default     = sum\n")
    config_file.write("aggregation_mutate_rate = 0.0\n")
    config_file.write("aggregation_options     = sum\n")
    # Now node bias options
    config_file.write("bias_init_mean          = 0.0\n")
    config_file.write("bias_init_stdev         = 1.0\n")
    config_file.write("bias_max_value          = 30.0\n")
    config_file.write("bias_min_value          = -30.0\n")
    config_file.write("bias_mutate_power       = 0.5\n")
    config_file.write("bias_mutate_rate        = 0.7\n")
    config_file.write("bias_replace_rate       = 0.1\n")
    # Now genome compatibility options
    config_file.write("compatibility_disjoint_coefficient = 1.0\n")
    config_file.write("compatibility_weight_coefficient   = 0.5\n")
    # Connection add/remove rates
    config_file.write("conn_add_prob           = 0.5\n")
    config_file.write("conn_delete_prob        = 0.5\n")
    # Connection enable options
    config_file.write("enabled_default         = True\n")
    config_file.write("enabled_mutate_rate     = 0.01\n")
    config_file.write("feed_forward            = True\n")
    config_file.write("initial_connection      = full\n")
    # Node add/remove rates
    config_file.write("node_add_prob           = 0.2\n")
    config_file.write("node_delete_prob        = 0.2\n")
    # Network Parameters
    config_file.write("num_hidden              = 0\n")
    config_file.write("num_inputs              = 3\n")
    config_file.write("num_outputs             = 1\n")
    # Node Response Options
    config_file.write("response_init_mean      = 1.0\n")
    config_file.write("response_init_stdev     = 0.0\n")
    config_file.write("response_max_value      = 30.0\n")
    config_file.write("response_min_value      = -30.0\n")
    config_file.write("response_mutate_power   = 0.0\n")
    config_file.write("response_mutate_rate    = 0.0\n")
    config_file.write("response_replace_rate   = 0.0\n")
    # Connection Weight Options
    config_file.write("weight_init_mean        = 0.0\n")
    config_file.write("weight_init_stdev       = 1.0\n")
    config_file.write("weight_max_value        = 30\n")
    config_file.write("weight_min_value        = -30\n")
    config_file.write("weight_mutate_power     = 0.5\n")
    config_file.write("weight_mutate_rate      = 0.8\n")
    config_file.write("weight_replace_rate     = 0.1\n\n")

    # Setting up the Default Species Set
    config_file.write("[DefaultSpeciesSet]\n")
    config_file.write("compatibility_threshold = 3.0\n\n")

    # Setting up the Default Stagnation
    config_file.write("[DefaultStagnation]\n")
    config_file.write("species_fitness_func = max\n")
    config_file.write("max_stagnation       = 20\n")
    config_file.write("species_elitism      = 2\n\n")

    # Setting up the Default Reproduction
    config_file.write("[DefaultReproduction]\n")
    config_file.write("elitism            = 2\n")
    config_file.write("survival_threshold = 0.2\n")

    # Close the file now that it has been changed
    config_file.close()

    # Run the file that contains the neural network configurations
    run(config_path, generations)

# ######IGNORE THE COMMENTED OUT CODE, IT IS A WORK IN PROGRESS IDEA
# def menu_window(win, plane, plane2, plane3, plane4, base):
#     # .blit() is basically just draw for pygame
#     # Place the background image center on the screen or (0,0) due to Pygame orientation
#     win.blit(pygame.transform.scale2x(pygame.image.load(os.path.join("Images", "background.png"))), (0, 0))
#     # call the method that will draw the ground into the game
#     base.draw(win)
#     # Calls the helper function to actually draw the plane
#     plane.draw_spin(win)
#     # Calls the helper function to actually draw the plane
#     plane2.draw_spin(win)
#     # Calls the helper function to actually draw the plane
#     plane3.draw_spin(win)
#     # Calls the helper function to actually draw the plane
#     plane4.draw_spin(win)
#     # Add Title Image to Game
#     win.blit(pygame.transform.scale(pygame.image.load(os.path.join("Images", "title.png")), (300, 150)), (100, 105))
#     # Updates the window with new visuals every frame
#     pygame.display.update()


# def user_inputs():
#     plane = Plane(220, 570)
#     plane2 = Plane(220, 50)
#     plane3 = Plane(380, 330)
#     plane4 = Plane(60, 290)
#     plane.spin_count = 0
#     plane2.spin_count = 21
#     plane3.spin_count = 10
#     plane4.spin_count = 31
#
#     base = Base(690)
#
#     win = pygame.display.set_mode((500, 800))
#     clock = pygame.time.Clock()
#
#     win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
#     population = 0
#     # Let the user increment the size of population to be used
#     increment_pop = pygame.Rect(192, 220, 20, 20)
#     # Draw da buttons
#     pygame.draw.rect(win, (30, 30, 30), increment_pop)
#     # Give the button some text
#     increment = STAT_FONT.render("+", 1, (255, 255, 255))
#     win.blit(increment, (210, 225))
#
#     # Let the user decrement the size of population to be used
#     decrement_pop = pygame.Rect(192, 220, 117, 30)
#     # Draw da buttons
#     pygame.draw.rect(win, (30, 30, 30), decrement_pop)
#     # Give the button some text
#     decrement = STAT_FONT.render("-", 1, (255, 255, 255))
#     win.blit(decrement, (320, 225))
#
#
#     back_to_menu = pygame.Rect(192, 320, 117, 30)
#     # Draw da buttons
#     pygame.draw.rect(win, (30, 30, 30), back_to_menu)
#     # Give the button some text
#     back = BUTTON_FONT.render("Back To Menu", 1, (255, 255, 255))
#     win.blit(back, (205, 325))
#     # Updates the window with new visuals every frame
#
#     # Make the bird move as it waits for the user to start the game
#     wait = True
#     while wait:
#         clock.tick(15)
#         # Moving and jumping of the bird
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 # 1 is the left mouse button, 2 is middle, 3 is right.
#                 if event.button == 1:
#                     if increment_pop.collidepoint(event.pos):
#                         pass
#                     elif decrement_pop.collidepoint(event.pos):
#                         pass
#                     elif back_to_menu.collidepoint(event.pos):
#                         pass
#
#         base.move()
#         menu_window(win, plane, plane2, plane3, plane4, base)


# Option button 1, regular game for the user to play
def option_two(win):
    # Let user choose what they finnna do
    #user_inputs()
    # Configuration(population, generations)
    configuration(15, 5)
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
    # Updates the window with new visuals every frame
    pygame.display.update()

    wait = True
    while wait:

        # Moving and jumping of the bird
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 1 is the left mouse button, 2 is middle, 3 is right.
                if event.button == 1:
                    if restart_game.collidepoint(event.pos):
                        # Whenever just the player is playing
                        option_two()
                    elif back_to_menu.collidepoint(event.pos):
                        # Whenever you want to watch the AI learn
                        wait = False

